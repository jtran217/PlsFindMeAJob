
export function formatDate(dateString: string): string {
  if (!dateString) return 'Date TBD'
  
  const date = new Date(dateString)
  
  if (isNaN(date.getTime())) return 'Invalid date'
  
  return date.toLocaleDateString('en-GB', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
