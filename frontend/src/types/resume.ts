/**
 * TypeScript type definitions for the enhanced resume system.
 * These types match the backend resume optimization schema.
 */

// Common nested types
export interface Website {
  url: string
  label: string
}

export interface ItemOptions {
  showLinkInTitle: boolean
}

// Picture configuration
export interface Picture {
  hidden: boolean
  url: string
  size: number
  rotation: number
  aspectRatio: number
  borderRadius: number
  borderColor: string
  borderWidth: number
  shadowColor: string
  shadowWidth: number
}

// Enhanced Basics section
export interface CustomField {
  id: string
  icon: string
  text: string
  link: string
}

export interface EnhancedBasics {
  name: string
  headline: string
  email: string
  phone: string
  location: string
  website: Website
  customFields: CustomField[]
}

// Summary section
export interface Summary {
  title: string
  columns: number
  hidden: boolean
  content: string
}

// Section items for different resume sections
export interface ProfileItem {
  id: string
  hidden: boolean
  icon: string
  network: string
  username: string
  website: Website
  options: ItemOptions
}

export interface ExperienceItem {
  id: string
  hidden: boolean
  company: string
  position: string
  location: string
  period: string
  website: Website
  description: string
  options: ItemOptions
}

export interface EducationItem {
  id: string
  hidden: boolean
  school: string
  degree: string
  area: string
  grade: string
  location: string
  period: string
  website: Website
  description: string
  options: ItemOptions
}

export interface ProjectItem {
  id: string
  hidden: boolean
  name: string
  period: string
  website: Website
  description: string
  options: ItemOptions
}

export interface SkillItem {
  id: string
  hidden: boolean
  icon: string
  name: string
  proficiency: string
  level: number
  keywords: string[]
  options: ItemOptions
}

export interface LanguageItem {
  id: string
  hidden: boolean
  language: string
  fluency: string
  level: number
  options: ItemOptions
}

export interface InterestItem {
  id: string
  hidden: boolean
  icon: string
  name: string
  keywords: string[]
  options: ItemOptions
}

export interface AwardItem {
  id: string
  hidden: boolean
  title: string
  awarder: string
  date: string
  website: Website
  description: string
  options: ItemOptions
}

export interface CertificationItem {
  id: string
  hidden: boolean
  title: string
  issuer: string
  date: string
  website: Website
  description: string
  options: ItemOptions
}

export interface PublicationItem {
  id: string
  hidden: boolean
  title: string
  publisher: string
  date: string
  website: Website
  description: string
  options: ItemOptions
}

export interface VolunteerItem {
  id: string
  hidden: boolean
  organization: string
  location: string
  period: string
  website: Website
  description: string
  options: ItemOptions
}

export interface ReferenceItem {
  id: string
  hidden: boolean
  name: string
  position: string
  website: Website
  phone: string
  description: string
  options: ItemOptions
}

// Section containers
export interface Section {
  title: string
  columns: number
  hidden: boolean
}

export interface ProfilesSection extends Section {
  items: ProfileItem[]
}

export interface ExperienceSection extends Section {
  items: ExperienceItem[]
}

export interface EducationSection extends Section {
  items: EducationItem[]
}

export interface ProjectsSection extends Section {
  items: ProjectItem[]
}

export interface SkillsSection extends Section {
  items: SkillItem[]
}

export interface LanguagesSection extends Section {
  items: LanguageItem[]
}

export interface InterestsSection extends Section {
  items: InterestItem[]
}

export interface AwardsSection extends Section {
  items: AwardItem[]
}

export interface CertificationsSection extends Section {
  items: CertificationItem[]
}

export interface PublicationsSection extends Section {
  items: PublicationItem[]
}

export interface VolunteerSection extends Section {
  items: VolunteerItem[]
}

export interface ReferencesSection extends Section {
  items: ReferenceItem[]
}

// All sections container
export interface ResumeSections {
  profiles: ProfilesSection
  experience: ExperienceSection
  education: EducationSection
  projects: ProjectsSection
  skills: SkillsSection
  languages: LanguagesSection
  interests: InterestsSection
  awards: AwardsSection
  certifications: CertificationsSection
  publications: PublicationsSection
  volunteer: VolunteerSection
  references: ReferencesSection
}

// Custom sections
export interface CustomSectionItem {
  id: string
  hidden: boolean
  recipient: string
  content: string
  options: ItemOptions
}

export interface CustomSection extends Section {
  id: string
  type: string
  items: CustomSectionItem[]
}

// Metadata configuration
export interface PageLayout {
  fullWidth: boolean
  main: string[]
  sidebar: string[]
}

export interface Layout {
  sidebarWidth: number
  pages: PageLayout[]
}

export interface CSS {
  enabled: boolean
  value: string
}

export interface Page {
  gapX: number
  gapY: number
  marginX: number
  marginY: number
  format: string
  locale: string
  hideIcons: boolean
}

export interface LevelConfig {
  icon: string
  type: string
}

export interface Colors {
  primary: string
  text: string
  background: string
}

export interface Design {
  level: LevelConfig
  colors: Colors
}

export interface Typography {
  fontFamily: string
  fontWeights: string[]
  fontSize: number
  lineHeight: number
}

export interface TypographySettings {
  body: Typography
  heading: Typography
}

export interface Metadata {
  template: string
  layout: Layout
  css: CSS
  page: Page
  design: Design
  typography: TypographySettings
  notes: string
}

// Main resume data container
export interface ResumeData {
  picture: Picture
  basics: EnhancedBasics
  summary: Summary
  sections: ResumeSections
  customSections: CustomSection[]
  metadata: Metadata
}

// Complete resume model
export interface Resume {
  name: string
  slug: string
  tags: string[]
  data: ResumeData
  isPublic: boolean
}

// Response types
export interface ResumeResponse {
  success: boolean
  message: string
  data?: Resume
}

export interface ResumeSaveResponse {
  success: boolean
  message: string
  errors?: Record<string, any>
}

// Default values for creating new items
export const defaultWebsite: Website = {
  url: '',
  label: ''
}

export const defaultItemOptions: ItemOptions = {
  showLinkInTitle: true
}

// Proficiency level options
export const proficiencyLevels = [
  'Beginner',
  'Intermediate', 
  'Advanced',
  'Expert'
] as const

export type ProficiencyLevel = typeof proficiencyLevels[number]

// Fluency level options
export const fluencyLevels = [
  'Elementary',
  'Limited Working',
  'Professional Working',
  'Full Professional',
  'Native or Bilingual'
] as const

export type FluencyLevel = typeof fluencyLevels[number]

// Popular social networks for profiles
export const socialNetworks = [
  'LinkedIn',
  'GitHub', 
  'Twitter',
  'Portfolio',
  'Personal Website',
  'Behance',
  'Dribbble',
  'Stack Overflow'
] as const

export type SocialNetwork = typeof socialNetworks[number]

// Utility functions for creating new items
export const createExperienceItem = (id?: string): ExperienceItem => ({
  id: id || `experience-${Date.now()}`,
  hidden: false,
  company: '',
  position: '',
  location: '',
  period: '',
  website: { ...defaultWebsite },
  description: '',
  options: { ...defaultItemOptions }
})

export const createEducationItem = (id?: string): EducationItem => ({
  id: id || `education-${Date.now()}`,
  hidden: false,
  school: '',
  degree: '',
  area: '',
  grade: '',
  location: '',
  period: '',
  website: { ...defaultWebsite },
  description: '',
  options: { ...defaultItemOptions }
})

export const createProjectItem = (id?: string): ProjectItem => ({
  id: id || `project-${Date.now()}`,
  hidden: false,
  name: '',
  period: '',
  website: { ...defaultWebsite },
  description: '',
  options: { ...defaultItemOptions }
})

export const createSkillItem = (id?: string): SkillItem => ({
  id: id || `skill-${Date.now()}`,
  hidden: false,
  icon: '',
  name: '',
  proficiency: 'Intermediate',
  level: 3,
  keywords: [],
  options: { ...defaultItemOptions }
})

export const createProfileItem = (id?: string): ProfileItem => ({
  id: id || `profile-${Date.now()}`,
  hidden: false,
  icon: '',
  network: '',
  username: '',
  website: { ...defaultWebsite },
  options: { ...defaultItemOptions }
})

export const createLanguageItem = (id?: string): LanguageItem => ({
  id: id || `language-${Date.now()}`,
  hidden: false,
  language: '',
  fluency: 'Elementary',
  level: 1,
  options: { ...defaultItemOptions }
})

export const createCertificationItem = (id?: string): CertificationItem => ({
  id: id || `certification-${Date.now()}`,
  hidden: false,
  title: '',
  issuer: '',
  date: '',
  website: { ...defaultWebsite },
  description: '',
  options: { ...defaultItemOptions }
})

export const createAwardItem = (id?: string): AwardItem => ({
  id: id || `award-${Date.now()}`,
  hidden: false,
  title: '',
  awarder: '',
  date: '',
  website: { ...defaultWebsite },
  description: '',
  options: { ...defaultItemOptions }
})

export const createInterestItem = (id?: string): InterestItem => ({
  id: id || `interest-${Date.now()}`,
  hidden: false,
  icon: '',
  name: '',
  keywords: [],
  options: { ...defaultItemOptions }
})