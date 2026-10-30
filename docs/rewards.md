# 2025Datawhale第4季度开源贡献者颁奖名单
<div class="reward-card-container">
  <div class="reward-card">
    <img 
      src="/rewards/2025Q4.png" 
      alt="2025年Q4季度开源贡献奖励" 
      class="reward-img"
      onerror="this.src='/rewards/default-reward.png'"
      loading="lazy"
    >
    <div class="reward-desc">
      感谢所有为开源社区做出杰出贡献的开发者们 🌟
    </div>
  </div>
</div> 

# 🏆 2025Datawhale第3季度开源贡献者颁奖名单
<div class="reward-card-container">
  <div class="reward-card">
    <img 
      src="/rewards/2025Q3.png" 
      alt="2025年Q3季度开源贡献奖励" 
      class="reward-img"
      onerror="this.src='/rewards/default-reward.png'"
      loading="lazy"
    >
    <div class="reward-desc">
      感谢所有为开源社区做出杰出贡献的开发者们 🌟
    </div>
  </div>
</div>

<style>
/* 统一样式类，替代内联样式，避免重复+提升可维护性 */
.reward-card-container {
  display: flex;
  justify-content: center;
  padding: 1.5rem 0;
}
.reward-card {
  background: var(--vp-c-bg);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 1rem;
  max-width: 95%;
}
.reward-img {
  width: 100%;
  height: auto;
  border-radius: 8px;
  object-fit: contain;
  max-height: 90vh;
}
.reward-desc {
  margin-top: 1rem;
  text-align: center;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

/* 响应式样式调整：适配移动设备（屏幕宽度≤768px） */
@media (max-width: 768px) {
  .reward-card-container {
    padding: 0.8rem 0; /* 无需!important，因为类样式优先级更可控 */
  }
  .reward-card {
    padding: 0.8rem;
    max-width: 98%;
  }
}
</style>