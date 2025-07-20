// eslint.config.js
import globals from "globals";
import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";

export default [
  // 1. Global ignores
  {
    ignores: ["dist/"],
  },

  // 2. Configuration for React/Browser files
  {
    files: ["src/**/*.{js,jsx}"], // Apply only to files in the 'src' folder
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    languageOptions: {
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
      globals: {
        ...globals.browser, // Use browser globals like 'window'
      },
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": "warn",
      "react/prop-types": "off",
    },
  },

  // 3. Configuration for Electron/Node.js files
  {
    files: ["electron.js", "preload.js"], // Apply only to these specific files
    languageOptions: {
      globals: {
        ...globals.node, // Use Node.js globals like 'require', '__dirname'
      },
    },
    rules: {
      ...js.configs.recommended.rules,
    },
  },
];
