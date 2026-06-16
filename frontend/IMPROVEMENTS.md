# Query UI React 前端 - 改进点清单

**文件位置**: `/home/mickey/.openclaw/mihua/tools/query_ui/frontend_original/`

**最后更新**: 2026-04-06

---

## 🔴 高优先级（必须修复）

### 1. **TypeScript 类型安全不足**
- ❌ `strict: false` 在 `tsconfig.json`（应启用 `strict: true`）
- ❌ 大量 `any` 类型（`types/index.ts`、组件 props、API 响应）
- ❌ 缺少接口定义（例如 `CompanyProfile` 不完整）

**影响**: 运行时错误无法在编译期捕获

**修复方案**:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noImplicitReturns": true
  }
}
```

### 2. **单体文件过大（违反单一职责）**
- ❌ `useCompanyData.ts` - 600+ 行，包含 15+ 个 hooks
- ❌ `CompanyDetail.tsx` - 264+ 行，包含所有子组件渲染
- ❌ `dataAdapter.ts` - 300+ 行，做太多事

**影响**: 难以测试、维护、复用

**修复方案**:
- 拆分 `useCompanyData.ts` → `hooks/team.ts`, `hooks/tech.ts`, `hooks/financials.ts` 等
- 拆分 `CompanyDetail.tsx` → 每个 Card 独立组件 + 容器组件

### 3. **API 层缺乏错误处理和重试**
```typescript
// 当前实现（api.ts）
export async function request<T>(endpoint: string, params?: Record<string, any>) {
  const res = await fetch(url);
  return await res.json();  // ❌ 未检查 res.ok
}
```

**缺失**:
- HTTP 状态码检查（4xx/5xx）
- 网络错误捕获
- 请求重试机制
- 请求取消（abort signal）

**修复方案**:
```typescript
export async function request<T>(endpoint: string, params?: Record<string, any>): Promise<ApiResponse<T>> {
  try {
    const res = await fetch(url, { signal, cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return { success: true, data: await res.json() };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
```

---

## 🟡 中优先级（强烈建议）

### 4. **性能问题**
- ❌ `CompanyDetail` 一次获取所有数据，没有懒加载/分片
- ❌ 所有图表/表格同时渲染，没有虚拟滚动
- ❌ 缺少 `React.memo` 和 `useMemo` 优化（已部分使用）
- ❌ 无代码分割（React.lazy + Suspense）

**修复方案**:
- 实现 Tab 懒加载：公司详情分 sections（团队、技术、财务等）
- 大型表格使用 `react-window` 或 `antd` 虚拟列表
- 将 `CompanyHeaderCard`、`FinancialDashboardCard` 等拆为独立 route 或 lazy load

### 5. **样式系统不统一**
- ❌ 内联样式混用（`style={{...}}`）
- ❌ 硬编码颜色（`#1F4E79` 出现在多个组件）
- ❌ 缺少全局样式变量（CSS-in-JS 或 CSS modules）

**修复方案**:
- 使用 Ant Design 主题系统统一品牌色
- 将内联样式提取为 styled-components 或 CSS modules
- 创建 `theme.ts` 集中管理颜色、间距、断点

### 6. **数据适配器过于复杂**
`dataAdapter.ts` 承担太多职责：
-  Revenue 提取逻辑复杂（尝试多个字段）
-  Team 数据格式处理（dict → array）
-  Financing timeline 构造
-  应该按实体拆分：`adapters/team.ts`, `adapters/financials.ts`, `adapters/valuation.ts`

---

## 🟢 低优先级（可选优化）

### 7. **测试覆盖率为 0%**
- ❌ 无单元测试（Jest/Vitest）
- ❌ 无集成测试
- ❌ 无 E2E 测试（Playwright/Cypress）

**建议**:
- 优先测试 `dataAdapter.ts`（纯函数）
- 测试关键 hooks：`useCompanyData`, `useTeamData`
- 添加组件 snapshot 测试

### 8. **国际化（i18n）不完整**
- ✅ 使用了 `antd` 中文 locale
- ❌ 但内容硬编码中文（"被投公司"、"投资机构"）
- ❌ 缺少英文支持

**建议**: 如果面向国际，添加 `react-i18next`

### 9. **可访问性（a11y）缺失**
- ❌ 缺少 ARIA labels（图表、图标按钮）
- ❌ 键盘导航未测试
- ❌ 颜色对比度可能不达标

**建议**: 使用 `@axe-core/react` 扫描

### 10. **搜索功能弱**
- ✅ 有 `/search` endpoint
- ❌ 前端仅简单输入框，无高级筛选
- ❌ 无搜索历史/联想
- ❌ 搜索结果无分页或无限滚动

**建议**:
- 添加搜索过滤器（行业、阶段、地域）
- 实现搜索建议（autocomplete）
- 虚拟列表渲染结果

---

## 📋 技术债务汇总

| 类别 | 问题 | 影响 | 预计工时 |
|------|------|------|----------|
| 类型安全 | strict: false + any 泛滥 | 运行时错误 | 2-3 天 |
| 代码组织 | 单体文件过大 | 难以维护 | 3-4 天 |
| API 层 | 无错误处理/重试 | 用户体验差 | 1-2 天 |
| 性能 | 无懒加载/虚拟滚动 | 渲染卡顿 | 2-3 天 |
| 样式 | 内联样式硬编码 | UI 不一致 | 1-2 天 |
| 测试 | 0%覆盖率 | 发布风险高 | 3-5 天 |
| 监控 | 无错误上报 | 问题难发现 | 1 天 |

**合计**: 13-20 个工作日

---

## 🎯 建议实施顺序

**Phase 1: 稳定性和类型安全（Week 1）**
1. 启用 TypeScript strict mode
2. 定义完整类型接口（CompanyProfile, Investor 等）
3. 修复所有 `any` 警告
4. 增强 API 错误处理

**Phase 2: 代码重构（Week 2）**
1. 拆分 `useCompanyData.ts` 为多个 hooks
2. 拆分 `CompanyDetail` 为容器+展示组件
3. 重构 `dataAdapter` 为按实体模块化

**Phase 3: 性能优化（Week 3）**
1. 实现 Tab 懒加载（公司详情 sections）
2. 表格虚拟滚动
3. 代码分割（React.lazy）

**Phase 4: 样式与一致性（Week 4）**
1. 提取主题配置
2. 替换内联样式
3. 统一间距/颜色系统

**Phase 5: 质量保障（Ongoing）**
1. 添加单元测试（覆盖率 > 80%）
2. E2E 测试关键路径
3. 可访问性审计

---

## 💡 快速改进（<1 天可完成）

1. ✅ 将品牌色 `#1F4E79` 提取为 CSS 变量或 Ant Design token
2. ✅ 添加全局错误边界（`ErrorBoundary` 已存在，但未在 `CompanyDetail` 使用）
3. ✅ `api.ts` 添加 `res.ok` 检查
4. ✅ 为 `useCompanyData` 添加缓存（避免重复请求同一公司）
5. ✅ 添加加载骨架屏统一组件（已存在 `LoadingSkeleton` 但未统一使用）

---

**准备状态**: ✅ 可作为 Coder 和 Frontend Agent 的训练文档
