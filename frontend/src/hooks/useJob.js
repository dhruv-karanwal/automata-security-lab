import { useState } from "react";
function useJob() {
  const [result, setResult] = useState(null), [error, setError] = useState(null), [loading, setLoading] = useState(false);
  return { result, error, loading, clear: () => {
    setResult(null);
    setError(null);
  }, run: async (fn) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await fn());
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  } };
}
export {
  useJob
};
