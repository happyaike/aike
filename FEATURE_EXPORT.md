# 导出功能设计文档

## 概述

导出功能允许用户将 SQL 查询结果以多种格式（CSV、JSON）下载到本地文件，便于数据分析、共享和归档。

## 现状分析

当前导出功能在 [Home.tsx](frontend/src/pages/Home.tsx) 中实现，存在以下问题：

- 导出逻辑与页面组件耦合，`exportToCSV` 和 `exportToJSON` 直接写在组件内部
- CSV 和 JSON 两条路径有大量重复逻辑（大数据量警告、Blob 创建、下载触发）
- 难以扩展新格式（如 Excel、SQL Insert 等）

## 设计思路

将导出流程拆分为三个清晰的子任务，每个子任务职责单一、可独立测试：

### 子任务 1：获取查询结果

**职责**：从当前应用状态中提取待导出的数据。

- 校验 `queryResult` 是否存在且 `rows.length > 0`，否则提示 "No data to export"
- 检测数据量：当行数超过阈值（当前 10,000 行）时，弹出确认对话框提醒用户
- 将 `queryResult`（含 `columns`、`rows`、`rowCount`）传递给格式化阶段

**输入**：`QueryResult | null`（组件状态）  
**输出**：`QueryResult`（校验通过后）或中止导出

### 子任务 2：格式化数据

**职责**：将查询结果转换为目标格式的字符串。

- **CSV 格式**：
  - 表头行：`columns.map(col => col.name).join(",")`
  - 数据行：逐行遍历 `rows`，对每个值做转义处理（逗号、引号、换行符）
  - 空值（`null`/`undefined`）输出为空字符串
- **JSON 格式**：
  - 直接 `JSON.stringify(rows, null, 2)`，保留原始数据类型

**输入**：`QueryResult`，目标格式标识（`"csv"` | `"json"`）  
**输出**：格式化后的字符串内容

### 子任务 3：创建文件

**职责**：将格式化字符串生成为文件并触发浏览器下载。

- 根据格式设置正确的 MIME type（`text/csv` / `application/json`）
- 创建 `Blob` 对象
- 通过 `URL.createObjectURL` 生成临时下载链接
- 文件命名规则：`${databaseName}_${timestamp}.${ext}`
- 触发 `<a>` 点击下载，完成后 `revokeObjectURL` 释放内存
- 提示导出成功消息

**输入**：格式化字符串，MIME type，文件扩展名  
**输出**：浏览器下载行为 + 成功提示

## 流程图

```
用户点击 EXPORT 按钮
        │
        ▼
┌───────────────────┐
│  1. 获取查询结果    │
│  - 校验数据存在     │
│  - 大数据量警告     │
└───────┬───────────┘
        │ QueryResult
        ▼
┌───────────────────┐
│  2. 格式化数据      │
│  - CSV / JSON 转换  │
│  - 值转义处理       │
└───────┬───────────┘
        │ string
        ▼
┌───────────────────┐
│  3. 创建文件        │
│  - Blob 创建        │
│  - 下载触发         │
│  - 内存释放         │
└───────────────────┘
```

## 涉及文件

| 文件 | 作用 |
|------|------|
| [Home.tsx](frontend/src/pages/Home.tsx) | 导出按钮 UI 与流程编排 |
| [FEATURE_EXPORT.md](FEATURE_EXPORT.md) | 本设计文档 |
