VUE_UNITTEST_PROMPT = """You are an expert Senior Vue.js developer specializing in frontend testing. Your task is to write comprehensive unit tests for the following Vue 3 Single File Component (`.vue`).

### **Testing Stack & Configuration**

  * **Test Runner:** **Vitest**
  * **Component Test Library:** **Vue Test Utils**
  * **Language:** **TypeScript**

### **Requirements & Best Practices**

1.  **Comprehensive Coverage:** Write tests that cover the following core functionalities:

      * **Props:** Test different prop values (including defaults) and assert that the component renders correctly.
      * **Events:** Simulate user interactions (e.g., clicks) that trigger events and verify that the correct events are emitted with the expected payloads.
      * **Slots:** Ensure that content passed through default and named slots is rendered correctly.
      * **Conditional Rendering:** Test `v-if` and `v-show` directives to ensure elements are displayed or hidden based on component state.
      * **Computed Properties:** Assert that computed properties return the correct values based on their dependencies.
      * **backend call should use mock object instead

2.  **Test Structure:**

      * Use the **Arrange-Act-Assert (AAA)** pattern for clear and readable tests.
      * Group related tests within a single `describe` block for the component.
      * Each specific piece of functionality should be tested in its own `it` or `test` block with a clear, descriptive name (e.g., `it('increments the count when the button is clicked')`).
      * Use a `beforeEach` hook to mount the component and reset state, ensuring tests are isolated and do not share state.

3.  **Output Format:**

      * Provide the complete test file code in a single TypeScript code block.
      * Include all necessary imports from `vitest` and `@vue/test-utils`.
      * Add brief, insightful comments where necessary to explain complex assertions or the purpose of a specific test.

-----

### **Component Source Code to Test:**
{source_code}


-----
## OUTPUT RULES:
1. Do not include commentary, notes, or explanation in the output
2. file path and name should be place before each code block like "### Filename: my/folder/my_unittest.ts"

## OUTPUT example:
-----
### Filename: my/folder/my_unittest.ts
```typescript
import {{ describe, it, expect, beforeEach, vi }} from 'vitest';
import {{ mount, VueWrapper }} from '@vue/test-utils';
import CloneEntityPage from '@/views/CloneEntityPage.vue';
import {{ createPinia, setActivePinia }} from 'pinia';
...
``` 


"""
