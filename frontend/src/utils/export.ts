/** 导出功能工具模块 — 实现「获取查询结果」和「格式化数据」子任务。 */

import type { QueryResult } from "../types/query";

// ============================================================
// 子任务 1：获取查询结果
// ============================================================

/** 大数据量警告阈值 */
export const LARGE_DATASET_THRESHOLD = 10000;

/** 校验结果类型 */
export type ExportValidationResult =
  | { status: "ok"; data: QueryResult }
  | { status: "needs_confirm"; data: QueryResult; rowCount: number }
  | { status: "empty" };

/**
 * 从组件状态中提取待导出的查询结果。
 *
 * - 若 queryResult 为空或无数据行，返回 `{ status: "empty" }`
 * - 若数据行数超过阈值，返回 `{ status: "needs_confirm" }` 由调用方弹出确认框
 * - 否则返回 `{ status: "ok" }` 直接进入格式化阶段
 */
export function getQueryResultForExport(
  queryResult: QueryResult | null
): ExportValidationResult {
  if (!queryResult || queryResult.rows.length === 0) {
    return { status: "empty" };
  }

  if (queryResult.rows.length > LARGE_DATASET_THRESHOLD) {
    return {
      status: "needs_confirm",
      data: queryResult,
      rowCount: queryResult.rowCount,
    };
  }

  return { status: "ok", data: queryResult };
}

// ============================================================
// 子任务 2：格式化数据
// ============================================================

/** 支持的导出格式 */
export type ExportFormat = "csv" | "json";

/**
 * 将单个值转义为 CSV 安全字符串。
 *
 * - null / undefined 输出为空字符串
 * - 包含逗号、引号、换行符的值用双引号包裹，内部引号翻倍转义
 */
function escapeCSVValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "";
  }

  const stringValue = String(value);

  if (
    stringValue.includes(",") ||
    stringValue.includes('"') ||
    stringValue.includes("\n")
  ) {
    return `"${stringValue.replace(/"/g, '""')}"`;
  }

  return stringValue;
}

/**
 * 将查询结果格式化为 CSV 字符串。
 *
 * - 第一行为表头：列名用逗号拼接
 * - 后续每行为数据：逐列取值并做 CSV 转义
 */
export function formatAsCSV(result: QueryResult): string {
  const headers = result.columns.map((col) => col.name);
  const lines: string[] = [headers.join(",")];

  for (const row of result.rows) {
    const values = headers.map((header) => escapeCSVValue(row[header]));
    lines.push(values.join(","));
  }

  return lines.join("\n");
}

/**
 * 将查询结果格式化为 JSON 字符串。
 *
 * - 直接序列化 rows 数组，保留原始数据类型
 * - 缩进 2 空格，便于阅读
 */
export function formatAsJSON(result: QueryResult): string {
  return JSON.stringify(result.rows, null, 2);
}

/**
 * 格式化调度函数：根据目标格式调用对应的格式化方法。
 */
export function formatQueryResult(
  result: QueryResult,
  format: ExportFormat
): string {
  switch (format) {
    case "csv":
      return formatAsCSV(result);
    case "json":
      return formatAsJSON(result);
  }
}
