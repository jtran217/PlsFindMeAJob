import {useState, useEffect} from 'react'
import type {Job} from '../data/fakeJobs'

export function useJobs(page = 1, limit = 10, status?: string) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error,setError] = useState<string | null>(null);
  const [total,setTotal] = useState(0);
  useEffect(() => {
    async function fetchJobs() {
      try{
        setLoading(true);
        const skip = (page - 1) * limit;
        let url = `http://localhost:8000/api/jobs?skip=${skip}&limit=${limit}`;
        if (status) {
          url += `&status=${status}`;
        }
        const response = await fetch(url);
        const {data, total} = await response.json();
        setJobs(data);
        setTotal(total);
        setLoading(false);
      }
      catch(err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      }
      finally{
        setLoading(false);
      }
    }
    fetchJobs();
  }, [page, limit, status]);

  return { jobs, loading,error,total};
}

export function useJobCounts() {
  const [counts, setCounts] = useState<{[key: string]: number}>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCounts() {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/jobs/count/status');
        const data = await response.json();
        setCounts(data);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    }
    fetchCounts();
  }, []);

  return { counts, loading, error };
}
