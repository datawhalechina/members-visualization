# 🏆 2025Datawhale第3季度开源贡献者颁奖名单

<!-- 外层容器：用于整体居中布局和设置上下内边距，营造页面呼吸感 -->
<div style="display: flex; justify-content: center; padding: 1.5rem 0;">
  <!-- 卡片容器：白色背景+阴影效果，增强内容层次感，设置最大宽度避免在宽屏上过度拉伸 -->
  <div style="background: var(--vp-c-bg); border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); padding: 1rem; max-width: 95%;">
    <img 
      src="/rewards/2025Q3.jpeg" 
      alt="2025年Q3季度开源贡献奖励" 
      style="width: 100%; height: auto; border-radius: 8px; object-fit: contain; max-height: 90vh;"
      onerror="this.src='/rewards/default-reward.png'"
      loading="lazy"
    >
    <!-- 说明文字：补充图片信息，感谢贡献者，与整体设计风格保持一致 -->
    <div style="margin-top: 1rem; text-align: center; color: var(--vp-c-text-2); font-size: 0.9rem;">
      感谢所有为开源社区做出杰出贡献的开发者们 🌟
    </div>
  </div>
</div>

<style>
/* 响应式样式调整：适配移动设备（屏幕宽度≤768px） */
@media (max-width: 768px) {
  /* 减小外层容器上下内边距，适应小屏显示 */
  div[style*="padding: 1.5rem 0"] {
    padding: 0.8rem 0 !important;
  }
  
  /* 减小卡片内边距，扩大显示占比，适配手机屏幕 */
  div[style*="padding: 1rem"] {
    padding: 0.8rem !important;
    max-width: 98% !important; /* 几乎占满屏幕宽度，提升小屏利用率 */
  }
}
</style>