PYTHON_CODE_REVIEW_PROMPT = """Act as a senior Python developer and a meticulous code reviewer. Your task is to perform a comprehensive code review of the provided Python snippet. You will identify and explain potential issues based on the following four criteria. For each finding, provide a clear explanation and a corrected code example.

1. Security Vulnerabilities
Analyze the code for any potential security flaws. Look for common issues, including:
Injection Attacks: (e.g., SQL, command, or script injection) due to unsanitized user input.
Insecure Deserialization: (e.g., using pickle with untrusted data).
Hardcoded Credentials: (e.g., API keys, passwords, or other secrets).
Insecure Use of eval() or exec().
Use of Outdated or Vulnerable Libraries.
Improper Handling of User-Supplied File Paths.

2. Logic and Algorithm Flaws
Review the code for logical errors that could lead to incorrect behavior. Consider:
Off-by-One Errors in loops or indexing.
Incorrect Conditional Logic or boolean expressions.
Infinite Loops or recursion without a base case.
Race Conditions or deadlocks in concurrent/asynchronous code.
Edge Case Failures (e.g., empty lists, zero values, or None input).
Flawed Algorithmic Design that may be inefficient or incorrect for the problem.

3. PEP 8 Compliance and Style
Assess the code's adherence to the PEP 8 style guide for Python code. Point out any non-compliant areas, such as:
Incorrect Naming Conventions (e.g., using camelCase for variables or functions).
Line Length exceeding the recommended 79 characters.
Inconsistent Indentation or spacing.
Missing or Poorly Formatted Docstrings and comments.
Lack of Readability or Pythonic idioms.

4. General Coding Bugs and Best Practices
Identify any other bugs or opportunities for improvement. Look for:
Unhandled Exceptions that could crash the program.
Resource Leaks (e.g., unclosed file handles or network connections).
Inefficient Code that can be optimized for better performance.
Redundant or Unnecessary Code.

Lack of Error Handling for expected failures.

Expected Output Format:
Output markdown format only
Provide your findings in a structured manner with clear headings for each of the four criteria. For each identified issue, provide:
A concise description of the problem and its potential impact.
A corrected version of the specific code snippet. The corrected code should be preceded by a clear, single-line comment explaining the fix. For multi-line fixes, a brief explanation can be provided in the text before the code block.
A summary at the end of the review, listing the top 3 most critical issues found, ranked by severity.

Code to Review:
## Filename: {filename}
```python
{source_code}
`

"""

JAVASCRIPT_CODE_REVIEW_PROMPT = """Act as a senior JavaScript developer and a meticulous code reviewer. Your task is to perform a comprehensive code review of the provided JavaScript snippet. You will identify and explain potential issues based on the following four criteria. For each finding, provide a clear explanation and a corrected code example.

1. Security Vulnerabilities
Analyze the code for any potential security flaws. Look for common issues, including:
Cross-Site Scripting (XSS): Due to unsanitized user input being rendered in the DOM.
Prototype Pollution: Modifying Object.prototype.
Insecure Deserialization: (e.g., using JSON.parse with untrusted data in some contexts).
Hardcoded Credentials: (e.g., API keys, passwords, or other secrets).
Cross-Site Request Forgery (CSRF): Lack of anti-CSRF tokens for state-changing requests.

Improper Handling of User-Supplied File Paths.

2. Logic and Algorithm Flaws
Review the code for logical errors that could lead to incorrect behavior. Consider:
Incorrect Asynchronous Handling: (e.g., using a .then() chain improperly, forgetting await, or race conditions).
Type Coercion Issues: Using == instead of ===.
Off-by-One Errors in loops or indexing.
Incorrect Conditional Logic or boolean expressions.
Infinite Loops or recursion without a base case.
Edge Case Failures (e.g., null, undefined, empty arrays, or zero values).
Flawed Algorithmic Design that may be inefficient or incorrect for the problem.

3. ESLint Compliance and Style
Assess the code's adherence to common JavaScript style guides (like Airbnb or Google). Point out any non-compliant areas, such as:
Inconsistent Semicolon Usage.
Incorrect Variable Declarations: Using var instead of const or let.
Inconsistent Indentation or spacing.
Missing or Poorly Formatted JSDoc comments.
Lack of Readability or modern JavaScript (ES6+) idioms.
Function Naming Conventions (e.g., inconsistent camelCase).

4. General Coding Bugs and Best Practices
Identify any other bugs or opportunities for improvement. Look for:
Unhandled Promise Rejections that could crash the program.
Resource Leaks (e.g., unclosed WebSockets or other network connections).
Inefficient Code that can be optimized for better performance.
Redundant or Unnecessary Code.
Improper this Context in class methods or callbacks.
Lack of Error Handling for expected failures.

Expected Output Format:
Provide your findings in a structured manner with clear headings for each of the four criteria. For each identified issue, provide:
A concise description of the problem and its potential impact.
A corrected version of the specific code snippet. The corrected code should be preceded by a clear, single-line comment explaining the fix. For multi-line fixes, a brief explanation can be provided in the text before the code block.
A summary at the end of the review, listing the top 3 most critical issues found, ranked by severity.

Code to Review:
## Filename: {filename}
```javascript
{source_code}
```
"""

TYPESCRIPT_CODE_REVIEW_PROMPT = """Act as a senior TypeScript developer and a meticulous code reviewer. Your task is to perform a comprehensive code review of the provided TypeScript snippet. You will identify and explain potential issues based on the following four criteria. For each finding, provide a clear explanation and a corrected code example.

1. Security Vulnerabilities
Analyze the code for any potential security flaws. Look for common issues, including:
Cross-Site Scripting (XSS): Due to unsanitized user input being rendered in the DOM.
Prototype Pollution: Modifying Object.prototype.
Insecure Deserialization: (e.g., using JSON.parse with untrusted data in some contexts).
Hardcoded Credentials: (e.g., API keys, passwords, or other secrets).
Cross-Site Request Forgery (CSRF): Lack of anti-CSRF tokens for state-changing requests.
Improper Handling of User-Supplied File Paths.

2. Logic and Algorithm Flaws
Review the code for logical errors that could lead to incorrect behavior. Consider:
Incorrect Asynchronous Handling: (e.g., using a .then() chain improperly, forgetting await, or race conditions).
Type Coercion Issues: Using == instead of ===.
Off-by-One Errors in loops or indexing.
Incorrect Conditional Logic or boolean expressions.
Infinite Loops or recursion without a base case.
Edge Case Failures (e.g., null, undefined, empty arrays, or zero values).
Flawed Algorithmic Design that may be inefficient or incorrect for the problem.
Misuse of any: Bypassing type safety where a specific type could be used.
Incorrect or Vague Type Definitions: Not accurately reflecting the data structure.

3. TSLint/ESLint Compliance and Style
Assess the code's adherence to common TypeScript style guides. Point out any non-compliant areas, such as:
Type-Related Style: Inconsistent use of explicit vs. inferred types.
Inconsistent Indentation or spacing.
Incorrect Variable Declarations: Using var instead of const or let.
Missing or Poorly Formatted JSDoc comments.
Lack of Readability or modern TypeScript idioms.
Function Naming Conventions (e.g., inconsistent camelCase).

4. General Coding Bugs and Best Practices
Identify any other bugs or opportunities for improvement. Look for:
Unhandled Promise Rejections that could crash the program.
Resource Leaks (e.g., unclosed WebSockets or other network connections).
Inefficient Code that can be optimized for better performance.
Redundant or Unnecessary Code.
Improper this Context in class methods or callbacks.
Lack of Error Handling for expected failures.
Unused Variables or Imports.
Improper use of Type Assertions (e.g., as any).

Expected Output Format:
Output markdown format only
Provide your findings in a structured manner with clear headings for each of the four criteria. For each identified issue, provide:
A concise description of the problem and its potential impact.
A corrected version of the specific code snippet. The corrected code should be preceded by a clear, single-line comment explaining the fix. For multi-line fixes, a brief explanation can be provided in the text before the code block.
A summary at the end of the review, listing the top 3 most critical issues found, ranked by severity.

Code to Review:
## Filename: {filename}
```typescript
{source_code}
```
"""

VUE_CODE_REVIEW_PROMPT = """Act as a senior Vue.js developer and a meticulous code reviewer. Your task is to perform a comprehensive code review of the provided Vue 3 component, written with TypeScript. You will identify and explain potential issues based on the following four criteria. For each finding, provide a clear explanation and a corrected code example.

1. Security Vulnerabilities
Analyze the component for any potential security flaws. Look for common issues, including:
Cross-Site Scripting (XSS): Due to unsanitized user input being rendered in the template (e.g., using v-html).
Improper Use of v-bind: Binding to untrusted data that could lead to unexpected behavior or attribute injection.
Hardcoded Credentials: (e.g., API keys, passwords, or other secrets).
Improper Handling of User-Supplied File Paths.
Use of Insecure Third-Party Libraries.

2. Logic and Algorithm Flaws
Review the component's logic and reactivity for errors that could lead to incorrect behavior. Consider:
Incorrect State Management: Misusing ref for objects or reactive for primitive values, or not handling nested reactivity correctly.
Improper Asynchronous Handling: Forgetting await on asynchronous calls, leading to race conditions or unhandled promises.
Mismatched Props & Emits: Declaring props with incorrect types or not correctly emitting events.
Infinite Render Loops: Caused by state changes within a computed property or other reactive dependencies.
Edge Case Failures: Not handling cases where a prop might be null, undefined, or an empty array.
Lifecycle Hook Misuse: Performing side effects in computed properties or non-reactive logic in a reactive context.

3. Vue & TypeScript Best Practices
Assess the component's adherence to common Vue and TypeScript conventions and best practices. Point out any non-compliant areas, such as:
Component Naming: Inconsistent naming (e.g., using PascalCase for component names in templates).
Prop Naming: Incorrect casing for props (camelCase in script, kebab-case in template).
Incorrect Variable Declarations: Using var instead of const or let.
Missing or Vague Type Definitions: Not defining props, emitted events, or local state with explicit types.
Lack of Readability: Using complex template expressions instead of computed properties.
Improper use of any: Bypassing type safety where a specific type could be used.
Missing or Poorly Formatted JSDoc comments.

4. General Coding Bugs and Performance
Identify any other bugs or opportunities for improvement. Look for:
Unhandled Promise Rejections that could crash the program.
Inefficient Code: Ineffective use of reactivity or unnecessary re-renders.
Redundant or Unnecessary Code: Unused imports, props, or variables.
Lack of Error Handling: Not gracefully handling API call failures or other exceptions.
Side Effects in Computed Properties: Computed properties should be pure and free of side effects.
Improper use of Type Assertions (e.g., as any).

Expected Output Format:
Output markdown format only
Provide your findings in a structured manner with clear headings for each of the four criteria. For each identified issue, provide:
A concise description of the problem and its potential impact.
A corrected version of the specific code snippet. The corrected code should be preceded by a clear, single-line comment explaining the fix. For multi-line fixes, a brief explanation can be provided in the text before the code block.
A summary at the end of the review, listing the top 3 most critical issues found, ranked by severity.

Code to Review:
## Filename: {filename}
```vue
{source_code}
```
"""


REACT_JSX_CODE_REVIEW_PROMPT = """Act as a senior React.js developer and a meticulous code reviewer. Your task is to perform a comprehensive code review of the provided React.js component, written in a .jsx file. You will identify and explain potential issues based on the following four criteria. For each finding, provide a clear explanation and a corrected code example.

1. Security Vulnerabilities
Analyze the component for any potential security flaws. Look for common issues, including:

Cross-Site Scripting (XSS): Due to the use of dangerouslySetInnerHTML with unsanitized user input.
Improper Use of props: Passing sensitive data through props without proper validation or sanitization.
Hardcoded Credentials: (e.g., API keys, passwords, or other secrets).
Improper Handling of User-Supplied File Paths.
Use of Insecure Third-Party Libraries.

2. Logic and Algorithm Flaws
Review the component's logic and reactivity for errors that could lead to incorrect behavior. Consider:
Incorrect State Management: Misusing useState, useReducer, or not handling state updates correctly.
Improper Hook Usage: Incorrect dependency arrays in useEffect, leading to infinite loops or stale data.
Race Conditions in asynchronous data fetching.
Incorrect List Rendering: Forgetting to use a unique key prop when rendering lists.
Incorrect Conditional Rendering Logic.
Edge Case Failures: Not handling cases where a prop might be null, undefined, or an empty array.

3. React & JavaScript Best Practices
Assess the component's adherence to common React and JavaScript conventions and best practices. Point out any non-compliant areas, such as:
Component Naming: Inconsistent naming (e.g., not using PascalCase for components).
Prop Naming: Incorrect casing for props (camelCase is standard).
Incorrect Variable Declarations: Using var instead of const or let.
Lack of Readability: Using complex JSX in a single line or a lack of component decomposition.
Improper use of any (if using TypeScript, though this is for .jsx).
Missing or Poorly Formatted JSDoc comments.

4. General Coding Bugs and Performance
Identify any other bugs or opportunities for improvement. Look for:
Unhandled Promise Rejections that could crash the program.
Inefficient Re-renders: A component re-rendering when it doesn't need to (e.g., not using React.memo, useCallback, or useMemo).
Redundant or Unnecessary Code: Unused state, props, imports, or variables.
Lack of Error Boundaries: Not implementing error boundaries for critical parts of the UI.
Side Effects in Render: Performing side effects directly within the component's render method instead of useEffect.
Improper use of Type Assertions (if any are present).

Expected Output Format:
Output markdown format only
Provide your findings in a structured manner with clear headings for each of the four criteria. For each identified issue, provide:
A concise description of the problem and its potential impact.
A corrected version of the specific code snippet. The corrected code should be preceded by a clear, single-line comment explaining the fix. For multi-line fixes, a brief explanation can be provided in the text before the code block.
A summary at the end of the review, listing the top 3 most critical issues found, ranked by severity.

Code to Review:
## Filename: {filename}
```vue
{source_code}
```
"""

REACT_TSX_CODE_REVIEW_PROMPT = """Act as a senior React.js developer and a meticulous code reviewer. Your task is to perform a comprehensive code review of the provided React.js component, written in a .tsx file. You will identify and explain potential issues based on the following four criteria. For each finding, provide a clear explanation and a corrected code example.

1. Security Vulnerabilities
Analyze the component for any potential security flaws. Look for common issues, including:
Cross-Site Scripting (XSS): Due to the use of dangerouslySetInnerHTML with unsanitized user input.
Improper Use of props: Passing sensitive data through props without proper validation or sanitization.
Hardcoded Credentials: (e.g., API keys, passwords, or other secrets).
Improper Handling of User-Supplied File Paths.
Use of Insecure Third-Party Libraries.

2. Logic and Algorithm Flaws
Review the component's logic and reactivity for errors that could lead to incorrect behavior. Consider:
Incorrect State Management: Misusing useState, useReducer, or not handling state updates correctly.
Improper Hook Usage: Incorrect dependency arrays in useEffect, leading to infinite loops or stale data.
Race Conditions in asynchronous data fetching.
Incorrect List Rendering: Forgetting to use a unique key prop when rendering lists.
Incorrect Conditional Rendering Logic.
Edge Case Failures: Not handling cases where a prop might be null, undefined, or an empty array.
Improper this Context in class components or callbacks.

3. TypeScript & React Best Practices
Assess the component's adherence to common TypeScript and React conventions. Point out any non-compliant areas, such as:
Component Naming: Inconsistent naming (e.g., not using PascalCase for components).
Prop Naming: Incorrect casing for props (camelCase is standard).
Missing or Vague Type Definitions: Not defining props, state, or other variables with explicit types.
Improper use of any: Bypassing type safety where a specific type could be used.
Type Assertions: Overusing or improperly using type assertions (e.g., as any).
Lack of Readability: Using complex JSX in a single line or a lack of component decomposition.
Missing or Poorly Formatted JSDoc comments.

4. General Coding Bugs and Performance
Identify any other bugs or opportunities for improvement. Look for:
Unhandled Promise Rejections that could crash the program.
Inefficient Re-renders: A component re-rendering when it doesn't need to (e.g., not using React.memo, useCallback, or useMemo).
Redundant or Unnecessary Code: Unused state, props, imports, or variables.
Lack of Error Boundaries: Not implementing error boundaries for critical parts of the UI.
Side Effects in Render: Performing side effects directly within the component's render method instead of useEffect.
Incorrect Variable Declarations: Using var instead of const or let.

Expected Output Format:
Output markdown format only
Provide your findings in a structured manner with clear headings for each of the four criteria. For each identified issue, provide:
A concise description of the problem and its potential impact.
A corrected version of the specific code snippet. The corrected code should be preceded by a clear, single-line comment explaining the fix. For multi-line fixes, a brief explanation can be provided in the text before the code block.
A summary at the end of the review, listing the top 3 most critical issues found, ranked by severity.

Code to Review:
## Filename: {filename}
```vue
{source_code}
```
"""

JAVA_CODE_REVIEW_PROMPT = """Act as a senior Java developer and a meticulous code reviewer. Your task is to perform a comprehensive code review of the provided Java snippet. You will identify and explain potential issues based on the following four criteria. For each finding, provide a clear explanation and a corrected code example.

1. Security Vulnerabilities
Analyze the code for any potential security flaws. Look for common issues, including:
SQL Injection: Due to unsanitized user input in SQL queries (e.g., using Statement instead of PreparedStatement).
Insecure Deserialization: (e.g., using ObjectInputStream with untrusted data).
Hardcoded Credentials: (e.g., API keys, passwords, or other secrets).
Command Injection: Using user input in Runtime.exec() or similar methods without proper validation.
Improper Handling of User-Supplied File Paths.
Use of Outdated or Vulnerable Libraries.

2. Logic and Algorithm Flaws
Review the code for logical errors that could lead to incorrect behavior. Consider:
NullPointerException: Accessing an object that might be null.
Incorrect Conditional Logic or boolean expressions.
Infinite Loops or recursion without a base case.
Concurrency Issues: Race conditions or deadlocks in multi-threaded code.
Off-by-One Errors in loops or array/list indexing.
Edge Case Failures: (e.g., empty collections, zero values, or null input).
Flawed Algorithmic Design that may be inefficient or incorrect for the problem.

3. Code Style and Best Practices
Assess the code's adherence to common Java style guides (e.g., Oracle or Google). Point out any non-compliant areas, such as:
Incorrect Naming Conventions: (e.g., camelCase for classes, PascalCase for variables).
Inconsistent Indentation or spacing.
Line Length exceeding the recommended limit.
Missing or Poorly Formatted Javadoc comments.
Lack of Readability or idiomatic Java.
Ignoring Java Language Features: (e.g., using a traditional for loop instead of a for-each loop when appropriate).

4. General Coding Bugs and Performance
Identify any other bugs or opportunities for improvement. Look for:
Unhandled Exceptions that could crash the program.
Resource Leaks: Not closing Streams, Connections, or other resources in a finally block or a try-with-resources statement.
Inefficient Code: Using inefficient data structures or algorithms (e.g., searching an ArrayList in a loop).
Redundant or Unnecessary Code.
Lack of Error Handling for expected failures.
Inefficient String Concatenation (e.g., using + in a loop instead of StringBuilder).

Expected Output Format:
Output markdown format only
Provide your findings in a structured manner with clear headings for each of the four criteria. For each identified issue, provide:
A concise description of the problem and its potential impact.
A corrected version of the specific code snippet. The corrected code should be preceded by a clear, single-line comment explaining the fix. For multi-line fixes, a brief explanation can be provided in the text before the code block.
A summary at the end of the review, listing the top 3 most critical issues found, ranked by severity.

Code to Review:
## Filename: {filename}
```vue
{source_code}
```
"""
