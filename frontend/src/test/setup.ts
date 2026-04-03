import "@testing-library/jest-dom/vitest";
import { afterAll, afterEach, beforeAll, vi } from "vitest";
import { server } from "@/test/server";

const localStorageMock = (() => {
  let store = new Map<string, string>();
  return {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => {
      store.set(key, String(value));
    },
    removeItem: (key: string) => {
      store.delete(key);
    },
    clear: () => {
      store = new Map<string, string>();
    },
  };
})();

beforeAll(() => {
  server.listen({ onUnhandledRequest: "error" });
  vi.stubGlobal("ResizeObserver", class {
    observe() {}
    unobserve() {}
    disconnect() {}
  });
  vi.stubGlobal("localStorage", localStorageMock);
  Object.defineProperty(window, "localStorage", {
    value: localStorageMock,
    configurable: true,
  });
});

afterEach(() => {
  server.resetHandlers();
  localStorageMock.clear();
});

afterAll(() => {
  server.close();
});
