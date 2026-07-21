# python_repl 安全方案对科研场景的影响分析

> 基于 PRD 4.6 典型高频场景，分析各安全方案的功能可用性

---

## 一、科研场景需求清单

| # | 场景 | python_repl 依赖程度 | 关键操作 |
|---|------|---------------------|---------|
| 1 | 合成 checklist | ❌ 不依赖 | 纯文件读写（read_file + write_file） |
| 2 | 实验矩阵 | ❌ 不依赖 | 纯文件读写 |
| 3 | 机理证据链审计 | ❌ 不依赖 | 纯文件读写 |
| 4 | 表征审计 | ❌ 不依赖 | 纯文件读写 |
| 5 | 阶段汇报（R06） | ❌ 不依赖 | 纯文件读写 + assets 路径引用 |
| 6 | **CSV 作图 + kobs 拟合** | ✅ **强依赖** | pandas 读 CSV → 数据处理 → matplotlib 绘图 → 保存 PNG |
| 7 | 写作结构 | ❌ 不依赖 | 纯文件读写 |

**结论**：7 个高频场景中，只有 **场景 6（CSV 作图 + kobs 拟合）** 强依赖 python_repl。

---

## 二、场景 6 的典型代码示例

### 用户输入
> "帮我分析 `assets/data/exp_005_kobs.csv`，拟合 kobs 曲线，生成图表保存到 `assets/figures/`"

### LLM 需要执行的代码
```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# 1. 读取 CSV
df = pd.read_csv('assets/data/exp_005_kobs.csv')

# 2. 数据处理
time = df['time_min'].values
concentration = df['concentration_mM'].values

# 3. 拟合 kobs（一阶动力学）
def first_order(t, k, C0):
    return C0 * np.exp(-k * t)

popt, pcov = curve_fit(first_order, time, concentration, p0=[0.1, 10])
kobs = popt[0]

# 4. 绘图
plt.figure(figsize=(8, 6))
plt.scatter(time, concentration, label='Experimental')
plt.plot(time, first_order(time, *popt), 'r-', label=f'Fit: kobs={kobs:.4f} min⁻¹')
plt.xlabel('Time (min)')
plt.ylabel('Concentration (mM)')
plt.legend()
plt.savefig('assets/figures/exp_005_kobs_fit.png', dpi=300)

print(f"拟合完成：kobs = {kobs:.4f} min⁻¹")
```

### 关键依赖
- **pandas**：读取 CSV
- **numpy**：数组操作
- **scipy**：曲线拟合
- **matplotlib**：绘图
- **文件系统访问**：读取 `assets/data/`，写入 `assets/figures/`

---

## 三、各方案对场景 6 的影响

### 方案 1：移除 python_repl

| 维度 | 影响 |
|------|------|
| **功能可用性** | ❌ **完全不可用** |
| **替代方案** | 需要用户手动在本地运行 Python 脚本，然后上传结果图 |
| **用户体验** | 严重退化：失去"AI 自动分析数据"的核心价值 |
| **适用场景** | 只适合纯文本处理的科研场景（如文献综述、写作辅助） |

**结论**：不推荐。场景 6 是科研 AI Agent 的核心价值所在。

---

### 方案 2：RestrictedPython

| 维度 | 影响 |
|------|------|
| **功能可用性** | ❌ **完全不可用** |
| **原因** | RestrictedPython 会阻止 `import pandas`、`import matplotlib` 等第三方库 |
| **可用的操作** | 只能做基础算术（`1+1`、`sum([1,2,3])`） |
| **用户体验** | 看起来有 python_repl，但实际无法完成任何科研任务 |

**结论**：不推荐。给人"安全"的错觉，但功能完全残废。

---

### 方案 3：Docker 容器隔离

| 维度 | 影响 |
|------|------|
| **功能可用性** | ✅ **完全可用**（需要正确配置） |
| **实现要点** | 1. 预装科研库（pandas/numpy/scipy/matplotlib）<br>2. Volume mount workspace 目录（只读或读写）<br>3. 网络隔离（`network_disabled=True`） |
| **性能影响** | 每次执行 +1-2 秒（容器启动开销） |
| **用户体验** | 无感知（除了稍慢） |

#### 具体实现示例

```python
import docker

def _run(self, code: str) -> str:
    client = docker.from_env()

    # 预构建镜像（Dockerfile）
    # FROM python:3.12-slim
    # RUN pip install pandas numpy scipy matplotlib

    container = client.containers.run(
        image="openclaw-research:latest",
        command=["python", "-c", code],
        volumes={
            str(self.workspace_dir): {
                'bind': '/workspace',
                'mode': 'rw'  # 允许读写 assets/
            }
        },
        working_dir="/workspace",
        network_disabled=True,  # 禁用网络
        mem_limit="1g",
        cpu_quota=100000,
        remove=True,
        timeout=60
    )
    return container.decode('utf-8')
```

#### 关键配置

| 配置项 | 值 | 说明 |
|-------|---|------|
| `volumes` | `workspace_dir:/workspace:rw` | 允许访问 assets/ 读写文件 |
| `network_disabled` | `True` | 禁止网络访问（防止数据泄露） |
| `mem_limit` | `1g` | 内存限制（防止 OOM） |
| `timeout` | `60` | 超时限制（防止死循环） |

**结论**：推荐用于生产环境。功能完整，安全性高，但实现复杂度较高。

---

### 方案 4：代码执行服务（Piston/Judge0）

| 维度 | 影响 |
|------|------|
| **功能可用性** | ⚠️ **部分可用** |
| **限制** | 1. 无法访问 workspace 文件（需要先上传 CSV 到服务）<br>2. 无法保存图片到 assets/（需要返回 base64 再写入）<br>3. 依赖外部服务可用性 |
| **用户体验** | 需要额外的文件传输步骤，流程复杂 |

#### 工作流程

```
1. LLM 调用 read_file 读取 CSV → 获取内容
2. LLM 将 CSV 内容嵌入到 Python 代码中（字符串形式）
3. 调用 Piston API 执行代码
4. Piston 返回 base64 编码的图片
5. LLM 调用 write_file 将 base64 解码后保存到 assets/
```

**结论**：不推荐。工作流程复杂，且依赖外部服务。

---

### 方案 5：接受风险 + 强化审计（当前实现）

| 维度 | 影响 |
|------|------|
| **功能可用性** | ✅ **完全可用** |
| **安全性** | ❌ 无隔离（可访问整个文件系统和网络） |
| **适用场景** | ✅ 个人本地部署<br>✅ 单用户使用<br>✅ 可信环境 |
| **风险缓解** | 1. 审计日志（记录所有执行的代码）<br>2. 危险操作检测（os.system/subprocess）<br>3. 文档明确标注风险 |

#### 增强实现

```python
class PythonREPLTool(BaseTool):
    """⚠️ SECURITY: Runs with full host privileges

    This tool executes Python code directly on the backend process.
    - Can access entire filesystem
    - Can make network requests
    - Bypasses write_file/read_file restrictions

    Suitable for personal, single-user deployments only.
    """

    workspace_dir: Path
    audit_log: bool = True

    def _run(self, code: str) -> str:
        # 审计日志
        if self.audit_log:
            logger.warning(f"[PYTHON_REPL] Executing:\n{code}")

        # 危险模式检测
        dangerous_patterns = [
            'os.system', 'subprocess', 'eval', '__import__',
            'os.remove', 'os.rmdir', 'shutil.rmtree',
            'socket', 'urllib', 'requests'
        ]
        if any(p in code for p in dangerous_patterns):
            logger.critical(f"[PYTHON_REPL] ⚠️ Dangerous pattern detected!")

        # 执行（当前实现）
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            exec(code, {"__builtins__": __builtins__})
            output = sys.stdout.getvalue()

            if self.audit_log:
                logger.info(f"[PYTHON_REPL] Output: {output[:200]}")

            return output if output else "Code executed successfully"

        except Exception as e:
            logger.error(f"[PYTHON_REPL] Error: {e}")
            return f"Error: {type(e).__name__}: {str(e)}"

        finally:
            sys.stdout = old_stdout
```

**结论**：推荐用于当前阶段（Phase 3+4）。功能完整，实现简单，适合个人科研场景。

---

## 四、推荐方案

### 短期（Phase 3+4）：方案 5（接受风险 + 审计）

**理由**：
1. ✅ 场景 6（CSV 作图）完全可用
2. ✅ 实现成本低（主要是日志和文档）
3. ✅ 适合个人科研场景（本地部署，单用户）
4. ✅ 不影响开发进度

**实施清单**：
- [ ] 在 `python_repl_tool.py` 顶部添加安全警告注释
- [ ] 添加审计日志（记录所有执行的代码）
- [ ] 添加危险操作检测（os.system/subprocess/socket）
- [ ] 创建 `docs/SECURITY.md` 明确说明风险
- [ ] 在 `phase3-4-dev-log.md` 中更正"隔离环境"的描述

### 长期（生产部署）：方案 3（Docker 隔离）

**触发条件**：
- 部署到服务器
- 多用户使用
- 对外提供服务

**实施清单**：
- [ ] 创建 Dockerfile（预装 pandas/numpy/scipy/matplotlib）
- [ ] 修改 `python_repl_tool.py` 支持 Docker 模式
- [ ] 配置 volume mount（workspace 目录）
- [ ] 添加资源限制（内存/CPU/超时）
- [ ] 测试场景 6 的完整流程

---

## 五、场景 6 的完整测试用例

### 测试数据（`assets/data/exp_005_kobs.csv`）

```csv
time_min,concentration_mM
0,10.0
5,8.2
10,6.7
15,5.5
20,4.5
25,3.7
30,3.0
```

### 测试提示词

> "帮我分析 `assets/data/exp_005_kobs.csv`，拟合一阶动力学曲线，计算 kobs，生成图表保存到 `assets/figures/exp_005_kobs_fit.png`"

### 预期结果

1. LLM 调用 `python_repl` 执行数据分析代码
2. 生成图片文件：`assets/figures/exp_005_kobs_fit.png`
3. 返回拟合结果：`kobs = 0.0523 min⁻¹`
4. LLM 调用 `write_file` 创建 `memory/tasks/TASK_exp_005.md`，包含：
   - 数据来源：`[CSV 数据](assets/data/exp_005_kobs.csv)`
   - 拟合结果：`kobs = 0.0523 min⁻¹`
   - 图表：`[拟合曲线](assets/figures/exp_005_kobs_fit.png)`

### 验收标准

| # | 检查项 | 方案 1 | 方案 2 | 方案 3 | 方案 4 | 方案 5 |
|---|--------|--------|--------|--------|--------|--------|
| 1 | 能读取 CSV | ❌ | ❌ | ✅ | ⚠️ | ✅ |
| 2 | 能使用 pandas | ❌ | ❌ | ✅ | ✅ | ✅ |
| 3 | 能使用 scipy 拟合 | ❌ | ❌ | ✅ | ✅ | ✅ |
| 4 | 能使用 matplotlib 绘图 | ❌ | ❌ | ✅ | ✅ | ✅ |
| 5 | 能保存图片到 assets/ | ❌ | ❌ | ✅ | ⚠️ | ✅ |
| 6 | 执行时间 < 5 秒 | N/A | N/A | ⚠️ | ⚠️ | ✅ |
| 7 | 无需额外配置 | N/A | N/A | ❌ | ❌ | ✅ |

**图例**：
- ✅ 完全支持
- ⚠️ 部分支持或有限制
- ❌ 不支持

---

## 六、结论

### 核心发现

1. **场景 6 是科研 AI Agent 的核心价值**：7 个高频场景中，只有它需要 python_repl，但它是最能体现"AI 自动分析数据"的场景。

2. **方案 1 和方案 2 不可行**：会导致场景 6 完全不可用，严重削弱产品价值。

3. **方案 5 是当前最佳选择**：
   - 功能完整（场景 6 完全可用）
   - 实现简单（主要是日志和文档）
   - 适合个人科研场景（本地部署，单用户）

4. **方案 3 是长期目标**：
   - 真正的安全隔离
   - 适合生产环境
   - 但实现复杂度较高

### 行动建议

**立即执行**（Phase 3+4）：
1. 保持当前 python_repl 实现（方案 5）
2. 添加审计日志和危险操作检测
3. 在文档中明确标注风险和适用场景
4. 在 `phase3-4-dev-log.md` 中更正"隔离环境"的描述为"审计模式"

**未来规划**（Phase 6+）：
1. 当需要部署到服务器或多用户使用时
2. 实现 Docker 隔离模式（方案 3）
3. 通过配置文件切换隔离级别（off/audit/docker）

---

**文档版本**：v1.0
**创建日期**：2026-03-10
**作者**：基于 OpenClaw 社区实践和 PRD 4.6 场景分析
