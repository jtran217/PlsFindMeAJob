import {useState, useEffect} from "react";

export function useJobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchJobs() {
      try {
        const response = await fetch("http://localhost:8000/api/jobs");

        if(!response.ok) {
          throw new Error("Failed to fetch jobs")
        }

        const data = await response.json()
        setJobs(data);

      } catch(err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    fetchJobs();
  },[])

  return {jobs,loading,error};
}
