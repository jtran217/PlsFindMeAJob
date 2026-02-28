import {useState, useEffect} from 'react'

export function useJobs(page = 1, limit = 10) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error,setError] = useState(null);
  const [total,setTotal] = useState(0);
  useEffect(() => {
    async function fetchJobs() {
      try{
        setLoading(true);
        const skip = (page - 1) * limit;
        const response = await fetch(
          `http://localhost:8000/api/jobs?skip=${skip}&limit=${limit}`
        );
        const {data, total} = await response.json();
        setJobs(data);
        setTotal(total);
        setLoading(false);
      }
      catch(err) {
        setError(err);
      }
      finally{
        setLoading(false);
      }
    }
    fetchJobs();
  }, [page, limit]);

  return { jobs, loading,error,total};
}
