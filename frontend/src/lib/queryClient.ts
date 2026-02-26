import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryKeyHashFn: (queryKey) => {
        return JSON.stringify(queryKey, (_, val) =>
          isPlainObject(val)
            ? Object.keys(val)
                .sort()
                .reduce((result, key) => {
                  result[key] = val[key];
                  return result;
                }, {} as any)
            : val
        );
      },
    },
  },
});

function isPlainObject(value: any) {
  if (Object.prototype.toString.call(value) !== '[object Object]') {
    return false;
  }

  const prototype = Object.getPrototypeOf(value);
  return prototype === null || prototype === Object.prototype;
}
