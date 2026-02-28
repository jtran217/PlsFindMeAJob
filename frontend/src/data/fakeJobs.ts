export interface Job {
  id: string;
  site: string;
  job_url: string;
  job_url_direct: string;
  title: string;
  company: string;
  location: string;
  date_posted: string;
  job_type: string;
  is_remote: boolean;
  description: string;
  company_url: string;
  company_url_direct: string;
  skills: string;
  experience_range: string;
  status:string;
}

export const fakeJobs: Job[] = [
  {
    id: "1",
    site: "LinkedIn",
    job_url: "https://linkedin.com/jobs/1",
    job_url_direct: "https://linkedin.com/jobs/1/direct",
    title: "Full Stack Software Engineer (Frontend Leaning)",
    company: "EIT Oxford",
    location: "Oxford",
    date_posted: "2026-02-10",
    job_type: "Full-time",
    is_remote: false,
    description:
      "We are looking for a Full Stack Software Engineer with a frontend focus to join our team. You will work on building and maintaining modern web applications using React, TypeScript, and Node.js. Responsibilities include designing component architectures, integrating REST and GraphQL APIs, writing unit and integration tests, and collaborating closely with product and design teams.\n\nYou'll contribute to our design system, improve performance and accessibility, and help shape engineering culture. We value clean code, thoughtful abstractions, and shipping with confidence.",
    company_url: "https://eitoxford.com",
    company_url_direct: "https://eitoxford.com/careers",
    skills: "React, TypeScript, Node.js, GraphQL, Tailwind CSS",
    experience_range: "2-4 years",
  },
  {
    id: "2",
    site: "Indeed",
    job_url: "https://indeed.com/jobs/2",
    job_url_direct: "https://indeed.com/jobs/2/direct",
    title: "Software Engineering Intern",
    company: "G-Research",
    location: "London",
    date_posted: "2026-02-09",
    job_type: "Internship",
    is_remote: false,
    description:
      "Join G-Research as a Software Engineering Intern and work alongside world-class engineers on high-performance systems. You'll gain exposure to distributed computing, large-scale data processing, and low-latency trading infrastructure.\n\nIdeal candidates are pursuing a degree in Computer Science or a related field and have strong fundamentals in data structures and algorithms.",
    company_url: "https://gresearch.co.uk",
    company_url_direct: "https://gresearch.co.uk/careers",
    skills: "Python, C#, Distributed Systems, Algorithms",
    experience_range: "0-1 years",
  },
  {
    id: "3",
    site: "Glassdoor",
    job_url: "https://glassdoor.com/jobs/3",
    job_url_direct: "https://glassdoor.com/jobs/3/direct",
    title: "Full Stack Developer - Retail Solutions",
    company: "Oliver Wyman",
    location: "Multiple Locations",
    date_posted: "2026-02-08",
    job_type: "Full-time",
    is_remote: false,
    description:
      "Oliver Wyman is seeking a Full Stack Developer to build and maintain retail analytics platforms. You will design scalable APIs, build interactive dashboards, and work with cross-functional teams to deliver data-driven insights.\n\nTech stack includes React, Python, PostgreSQL, and AWS. Experience with CI/CD pipelines and containerization is a plus.",
    company_url: "https://oliverwyman.com",
    company_url_direct: "https://oliverwyman.com/careers",
    skills: "React, Python, PostgreSQL, AWS, Docker",
    experience_range: "2-5 years",
  },
  {
    id: "4",
    site: "LinkedIn",
    job_url: "https://linkedin.com/jobs/4",
    job_url_direct: "https://linkedin.com/jobs/4/direct",
    title: "Software Engineer",
    company: "Lloyds Banking Group",
    location: "Leeds",
    date_posted: "2026-02-07",
    job_type: "Full-time",
    is_remote: false,
    description:
      "Lloyds Banking Group is hiring a Software Engineer to work on core banking platforms. You will develop microservices, integrate with legacy systems, and support cloud migration initiatives.\n\nStrong experience with Java or Kotlin, Spring Boot, and event-driven architectures is required.",
    company_url: "https://lloydsbankinggroup.com",
    company_url_direct: "https://lloydsbankinggroup.com/careers",
    skills: "Java, Spring Boot, Kafka, Kubernetes, SQL",
    experience_range: "3-5 years",
  },
  {
    id: "5",
    site: "Indeed",
    job_url: "https://indeed.com/jobs/5",
    job_url_direct: "https://indeed.com/jobs/5/direct",
    title: "Web UI Developer",
    company: "Deutsche Bank",
    location: "London",
    date_posted: "2026-02-06",
    job_type: "Contract",
    is_remote: false,
    description:
      "Deutsche Bank is looking for a Web UI Developer to build internal trading dashboards. You'll work with Angular, RxJS, and WebSockets to deliver real-time data visualizations.\n\nExperience in financial services and familiarity with FIX protocol or market data feeds is a strong advantage.",
    company_url: "https://db.com",
    company_url_direct: "https://db.com/careers",
    skills: "Angular, TypeScript, RxJS, WebSockets, D3.js",
    experience_range: "3-6 years",
  },
  {
    id: "6",
    site: "Glassdoor",
    job_url: "https://glassdoor.com/jobs/6",
    job_url_direct: "https://glassdoor.com/jobs/6/direct",
    title: "Platform Engineer",
    company: "Caspian One Ltd",
    location: "Glasgow, SCT, GB",
    date_posted: "2026-02-05",
    job_type: "Full-time",
    is_remote: true,
    description:
      "Caspian One is hiring a Platform Engineer to build and maintain cloud infrastructure on AWS and GCP. You'll work on Terraform modules, CI/CD pipelines, monitoring, and container orchestration with Kubernetes.\n\nWe value infrastructure-as-code best practices, security-first thinking, and clear documentation.",
    company_url: "https://caspianone.com",
    company_url_direct: "https://caspianone.com/careers",
    skills: "Terraform, AWS, GCP, Kubernetes, Python",
    experience_range: "2-4 years",
  },
  {
    id: "7",
    site: "LinkedIn",
    job_url: "https://linkedin.com/jobs/7",
    job_url_direct: "https://linkedin.com/jobs/7/direct",
    title: "DevOps Engineer",
    company: "Digital Applications International",
    location: "Stockport, ENG",
    date_posted: "2026-02-04",
    job_type: "Full-time",
    is_remote: false,
    description:
      "Join our DevOps team to automate infrastructure, manage deployments, and improve system reliability. You'll work with Jenkins, Docker, Kubernetes, and cloud platforms.\n\nStrong scripting skills in Bash or Python and experience with monitoring tools like Prometheus and Grafana are expected.",
    company_url: "https://digital-ai.com",
    company_url_direct: "https://digital-ai.com/careers",
    skills: "Docker, Kubernetes, Jenkins, Prometheus, Bash",
    experience_range: "2-4 years",
  },
  {
    id: "8",
    site: "Indeed",
    job_url: "https://indeed.com/jobs/8",
    job_url_direct: "https://indeed.com/jobs/8/direct",
    title: "Software Dev Intern - AI / Machine Learning",
    company: "Amazon",
    location: "London, ENG, GB",
    date_posted: "2026-02-03",
    job_type: "Internship",
    is_remote: false,
    description:
      "Amazon is looking for a Software Development Intern to work on AI/ML initiatives. You'll build data pipelines, train and evaluate models, and contribute to production ML systems.\n\nCandidates should have experience with Python, PyTorch or TensorFlow, and a strong foundation in statistics and linear algebra.",
    company_url: "https://amazon.com",
    company_url_direct: "https://amazon.com/jobs",
    skills: "Python, PyTorch, TensorFlow, SQL, AWS SageMaker",
    experience_range: "0-1 years",
  },
];
