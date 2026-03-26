/// <reference types="vite/client" />

declare module "sql.js" {
  export interface SqlJsStatic {
    Database: new (data?: ArrayLike<number>) => Database;
  }

  export interface Database {
    prepare(sql: string): Statement;
    run(sql: string, params?: unknown[]): Database;
    exec(sql: string): QueryExecResult[];
    close(): void;
  }

  export interface Statement {
    bind(params?: Record<string, unknown> | unknown[]): boolean;
    step(): boolean;
    getAsObject(): Record<string, unknown>;
    free(): void;
  }

  export interface QueryExecResult {
    columns: string[];
    values: unknown[][];
  }

  export default function initSqlJs(config?: {
    locateFile?: (file: string) => string;
  }): Promise<SqlJsStatic>;
}
