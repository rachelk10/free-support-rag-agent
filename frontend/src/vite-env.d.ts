// Type declarations for Vite's import.meta.env
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  // add more env variables as needed
  [key: string]: string | undefined;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
