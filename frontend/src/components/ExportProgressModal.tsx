/** 导出进度可视化组件 — 用 Steps 展示三个子任务的实时执行状态。 */

import React from "react";
import { Modal, Steps, Typography, Result } from "antd";
import {
  DatabaseOutlined,
  FileTextOutlined,
  DownloadOutlined,
  CheckCircleFilled,
} from "@ant-design/icons";
import type { ExportFormat } from "../utils/export";

const { Text } = Typography;

/** 导出步骤索引 */
export type ExportStep = 0 | 1 | 2 | 3;

/** 每个步骤的详情信息 */
export interface ExportStepInfo {
  rowCount?: number;
  contentSize?: string;
  fileName?: string;
  format?: ExportFormat;
}

interface ExportProgressModalProps {
  open: boolean;
  currentStep: ExportStep;
  stepInfo: ExportStepInfo;
  onClose: () => void;
}

/** 步骤定义 */
const STEP_CONFIG = [
  {
    title: "获取查询结果",
    icon: <DatabaseOutlined />,
    description: "校验数据并提取查询结果",
  },
  {
    title: "格式化数据",
    icon: <FileTextOutlined />,
    description: "转换为目标格式（CSV / JSON）",
  },
  {
    title: "创建文件",
    icon: <DownloadOutlined />,
    description: "生成文件并触发下载",
  },
];

export const ExportProgressModal: React.FC<ExportProgressModalProps> = ({
  open,
  currentStep,
  stepInfo,
  onClose,
}) => {
  // currentStep=3 表示全部完成
  const isDone = currentStep >= 3;
  // Steps 组件的 current 属性最大为 2（三步），超过时取 2
  const stepsCurrent = Math.min(currentStep, 2);

  // 根据步骤渲染详情描述
  const renderStepDescription = (index: number) => {
    if (currentStep <= index) return null;

    switch (index) {
      case 0:
        return (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {stepInfo.rowCount} 行数据已就绪
          </Text>
        );
      case 1:
        return (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {stepInfo.format?.toUpperCase()} 格式 • {stepInfo.contentSize}
          </Text>
        );
      case 2:
        return (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {stepInfo.fileName}
          </Text>
        );
      default:
        return null;
    }
  };

  return (
    <Modal
      open={open}
      onCancel={onClose}
      footer={null}
      width={520}
      centered
      closable={isDone}
      maskClosable={false}
      title={
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {isDone ? (
            <CheckCircleFilled style={{ color: "#16aa98" }} />
          ) : (
            <DownloadOutlined style={{ color: "#000000" }} />
          )}
          <span>{isDone ? "导出完成" : "正在导出..."}</span>
        </div>
      }
    >
      {isDone ? (
        <Result
          status="success"
          title={`已导出 ${stepInfo.rowCount} 行数据`}
          subTitle={
            <div>
              <div>格式：{stepInfo.format?.toUpperCase()}</div>
              <div>文件：{stepInfo.fileName}</div>
              <div>大小：{stepInfo.contentSize}</div>
            </div>
          }
          style={{ padding: "16px 0" }}
        />
      ) : (
        <div style={{ padding: "24px 0 8px" }}>
          <Steps
            current={stepsCurrent}
            direction="vertical"
            size="small"
            items={STEP_CONFIG.map((step, index) => ({
              title: (
                <span style={{ fontSize: 14, fontWeight: 600 }}>
                  {step.title}
                </span>
              ),
              description: (
                <div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {step.description}
                  </Text>
                  <div style={{ marginTop: 2 }}>
                    {renderStepDescription(index)}
                  </div>
                </div>
              ),
              icon: step.icon,
            }))}
          />
        </div>
      )}
    </Modal>
  );
};
