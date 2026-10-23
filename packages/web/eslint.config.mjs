import parser from "@typescript-eslint/parser";
import plugin from "@typescript-eslint/eslint-plugin";

export default [
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: { parser },
  },
  {
    plugins: { "@typescript-eslint": plugin },
    rules: {
      "@typescript-eslint/no-unused-vars": "warn",
    },
  },
  {
    ignores: ["node_modules", ".next", "out", "build", "dist"],
  },
];
