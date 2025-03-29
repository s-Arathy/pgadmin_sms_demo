const globals = require('globals');
const js = require('@eslint/js');
const reactPlugin = require('eslint-plugin-react');
const babelPlugin = require('@babel/eslint-plugin');
const babelParser = require('@babel/eslint-parser');
const tsPlugin = require('@typescript-eslint/eslint-plugin');
const tsParser = require('@typescript-eslint/parser');
const jestPlugin = require('eslint-plugin-jest');
const unusedImportsPlugin = require('eslint-plugin-unused-imports');

module.exports = [
  {
    ignores: [
      '**/generated',
      '**/node_modules',
      '**/vendor',
      '**/templates/',
      '**/templates\\',
      '**/ycache',
      '**/regression/htmlcov',
    ],
  },
  js.configs.recommended,
  {
    files: ['**/*.{js,jsx,mjs,cjs,ts,tsx}'],
    languageOptions: {
      parser: babelParser,
      ecmaVersion: 'latest',
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
        requireConfigFile: false,
        babelOptions: {
          plugins: [
            '@babel/plugin-syntax-jsx',
            '@babel/plugin-proposal-class-properties',
          ],
        },
        ...reactPlugin.configs.recommended.parserOptions,
        ...reactPlugin.configs['jsx-runtime'].parserOptions,
      },
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.es2017,
        ...globals.amd,
        '_': 'readonly',
        'module': 'readonly',
        '__dirname': 'readonly',
        'global': 'readonly',
        'jest': 'readonly',
        'process': 'readonly',
      },
    },
    plugins: {
      'react': reactPlugin,
      '@babel': babelPlugin,
      'unused-imports': unusedImportsPlugin,
    },
    rules: {
      'indent': ['error', 2],
      'linebreak-style': ['error', 'windows'],
      'quotes': ['error', 'single'],
      'semi': ['error', 'always'],
      'comma-dangle': ['error', 'only-multiline'],
      'no-console': ['error', { allow: ['warn', 'error', 'trace'] }],
      'no-useless-escape': 'off',
      'no-prototype-builtins': 'off',
      'no-global-assign': 'off',
      'no-import-assign': 'off',
      ...reactPlugin.configs.recommended.rules,
      ...reactPlugin.configs['jsx-runtime'].rules,
      'react/jsx-uses-react': 'error',
      'react/jsx-uses-vars': 'error',
      'no-unused-vars': 'off',
      'unused-imports/no-unused-imports': 'error',
      'unused-imports/no-unused-vars': [
        'warn',
        {
          'vars': 'all',
          'varsIgnorePattern': '^_',
          'args': 'after-used',
          'argsIgnorePattern': '^_'
        },
      ]
    },
    settings: {
      'react': {
        'version': 'detect',
      },
    },
  },
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsParser,
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
    },
    rules: {
      'no-unused-vars': 'off',
      'no-undef': 'off',
      '@typescript-eslint/no-unused-vars': ['error'],
      '@typescript-eslint/no-explicit-any': ['off'],
      '@typescript-eslint/no-this-alias': ['off'],
    }
  },
  {
    files: ['**/*{spec,test}.{js,jsx}', './regression/javascript/**/*.{js}'],
    ...jestPlugin.configs['flat/recommended'],
    rules: {
      ...jestPlugin.configs['flat/recommended'].rules,
      'jest/prefer-expect-assertions': 'off',
      'jest/expect-expect': 'off',
      'jest/no-identical-title': 'off',
      'jest/no-done-callback': 'off',
      'jest/no-conditional-expect': 'off',
      'jest/valid-title': 'off',
    },
  },
]; 