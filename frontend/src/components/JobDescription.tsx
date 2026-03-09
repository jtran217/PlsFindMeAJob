import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter'
import { dark } from 'react-syntax-highlighter/dist/esm/styles/hljs'

// Import only languages commonly found in job descriptions to optimize bundle
import javascript from 'react-syntax-highlighter/dist/esm/languages/hljs/javascript'
import typescript from 'react-syntax-highlighter/dist/esm/languages/hljs/typescript'
import python from 'react-syntax-highlighter/dist/esm/languages/hljs/python'
import sql from 'react-syntax-highlighter/dist/esm/languages/hljs/sql'
import bash from 'react-syntax-highlighter/dist/esm/languages/hljs/bash'
import yaml from 'react-syntax-highlighter/dist/esm/languages/hljs/yaml'
import json from 'react-syntax-highlighter/dist/esm/languages/hljs/json'
import dockerfile from 'react-syntax-highlighter/dist/esm/languages/hljs/dockerfile'

// Register languages with SyntaxHighlighter
SyntaxHighlighter.registerLanguage('javascript', javascript)
SyntaxHighlighter.registerLanguage('js', javascript)
SyntaxHighlighter.registerLanguage('typescript', typescript)
SyntaxHighlighter.registerLanguage('ts', typescript)
SyntaxHighlighter.registerLanguage('python', python)
SyntaxHighlighter.registerLanguage('sql', sql)
SyntaxHighlighter.registerLanguage('bash', bash)
SyntaxHighlighter.registerLanguage('shell', bash)
SyntaxHighlighter.registerLanguage('yaml', yaml)
SyntaxHighlighter.registerLanguage('yml', yaml)
SyntaxHighlighter.registerLanguage('json', json)
SyntaxHighlighter.registerLanguage('dockerfile', dockerfile)

interface JobDescriptionProps {
  content: string | null
  className?: string
}

export function JobDescription({ content, className = '' }: JobDescriptionProps) {
  if (!content) {
    return (
      <div className="text-slate-400 italic">
        No description available
      </div>
    )
  }

  return (
    <div className={`prose prose-invert max-w-none ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize]}
        components={{
          // Headers with proper hierarchy and dark theme styling
          h1: ({ children }) => (
            <h1 className="text-2xl font-bold text-slate-100 mb-4 mt-6 first:mt-0">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-bold text-slate-100 mb-3 mt-5 first:mt-0">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-semibold text-slate-100 mb-3 mt-4 first:mt-0">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-base font-semibold text-slate-100 mb-2 mt-3 first:mt-0">
              {children}
            </h4>
          ),
          h5: ({ children }) => (
            <h5 className="text-sm font-semibold text-slate-100 mb-2 mt-3 first:mt-0">
              {children}
            </h5>
          ),
          h6: ({ children }) => (
            <h6 className="text-xs font-semibold text-slate-100 mb-2 mt-3 first:mt-0 uppercase tracking-wide">
              {children}
            </h6>
          ),

          // Paragraphs with proper spacing
          p: ({ children }) => (
            <p className="text-slate-200 mb-4 leading-relaxed">
              {children}
            </p>
          ),

          // Strong/bold text
          strong: ({ children }) => (
            <strong className="font-semibold text-white">
              {children}
            </strong>
          ),

          // Emphasis/italic text
          em: ({ children }) => (
            <em className="italic text-slate-100">
              {children}
            </em>
          ),

          // Links with hover effects
          a: ({ children, href }) => (
            <a
              href={href}
              className="text-indigo-400 hover:text-indigo-300 underline transition-colors duration-200"
              target="_blank"
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),

          // Lists with proper styling
          ul: ({ children }) => (
            <ul className="list-disc list-inside mb-4 space-y-2 text-slate-200">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside mb-4 space-y-2 text-slate-200">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-slate-200">
              {children}
            </li>
          ),

          // Blockquotes
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-indigo-500 pl-4 py-2 mb-4 text-slate-300 italic bg-slate-800/30 rounded-r">
              {children}
            </blockquote>
          ),

          // Horizontal rules
          hr: () => (
            <hr className="border-t border-slate-600 my-6" />
          ),

          // Code blocks and inline code with syntax highlighting
          code: ({ className, children, ...props }: any) => {
            const match = /language-(\w+)/.exec(className || '')
            const code = String(children).replace(/\n$/, '')
            
            return className && match ? (
              <div className="mb-4">
                <SyntaxHighlighter
                  style={dark}
                  language={match[1]}
                  PreTag="div"
                  className="rounded-lg border border-slate-700"
                  customStyle={{
                    padding: '1rem',
                    backgroundColor: '#1e293b',
                    fontSize: '0.875rem',
                    lineHeight: '1.5',
                  }}
                  {...props}
                >
                  {code}
                </SyntaxHighlighter>
              </div>
            ) : (
              <code 
                className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded text-sm font-mono"
                {...props}
              >
                {children}
              </code>
            )
          },

          // Pre blocks (fallback for code without language)
          pre: ({ children }) => (
            <pre className="bg-slate-800 text-slate-300 p-4 rounded-lg mb-4 overflow-x-auto text-sm font-mono leading-relaxed border border-slate-700">
              {children}
            </pre>
          ),

          // Tables (if any job descriptions have them)
          table: ({ children }) => (
            <div className="overflow-x-auto mb-4">
              <table className="min-w-full border-collapse border border-slate-600">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-slate-700">
              {children}
            </thead>
          ),
          tbody: ({ children }) => (
            <tbody>
              {children}
            </tbody>
          ),
          tr: ({ children }) => (
            <tr className="border-b border-slate-600">
              {children}
            </tr>
          ),
          th: ({ children }) => (
            <th className="border border-slate-600 px-4 py-2 text-left font-semibold text-slate-100">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border border-slate-600 px-4 py-2 text-slate-200">
              {children}
            </td>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}