import {useState, useEffect} from 'react';


type Basics = {
  name: string
  email: string
  phone: string
}

type Experience = {
  company?: string
  position?: string
  start_date?: string
  end_date?: string
  location?: string
  bullets?: string[]
}

type Education = {
  institution?: string
  degree?: string
  start_date?: string
  end_date?: string
}

type Project = {
  name?: string
  description?: string
}

type Profile = {
  basics: Basics
  experiences: Experience[]
  education: Education[]
  skills: string[]
  projects: Project[]
}

const emptyProfile: Profile = {
  basics: {
    name: "",
    email: "",
    phone: ""
  },
  experiences: [],
  education: [],
  skills: [],
  projects: []
}

export function useProfile() {
  const [profile,setProfile] = useState<Profile>(emptyProfile);
  const [error,setError] = useState(null);
  const [loading,setLoading] = useState(false);

  useEffect(()=>{
    async function fetchProfile() {
      try {
        setLoading(true);
        const data = await fetch('http://localhost:8000/api/profile').then(res=>res.json());
        setProfile(data);
        setLoading(false);
      } catch(err) {
        setError(err);
        setLoading(false);
      } 
  }
    fetchProfile();

  },[])
  
  const saveProfile = async(updatedProfile:Profile) => {
    setProfile(updatedProfile)

    try {
      await fetch('http://localhost:8000/api/profile', {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(updatedProfile)
      })
      
    } catch(err){
      setError(err);
      console.error("Failed to save profile:", err);
    }
  }


  return {profile,setProfile, loading, error, saveProfile};

}
