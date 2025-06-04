// 为 .vue 单文件组件提供类型定义，确保 TypeScript 能正确解析和类型检查 Vue 组件。

declare module '*.vue' {
  import { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}