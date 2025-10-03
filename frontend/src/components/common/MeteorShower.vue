<template>
  <!-- 这个SVG层会覆盖整个屏幕，但对鼠标事件透明 -->
  <svg class="meteor-svg-layer">
    <!-- 
      在这里定义一个径向渐变，作为所有流星的“笔刷”。
      它从中心的不透明金色(var(--primary-color))，向外渐变为完全透明。
      这将创造出流星头部最亮，尾部逐渐消失的辉光效果。
    -->
    <defs>
      <radialGradient :id="gradientId">
        <stop offset="0%" :stop-color="`rgba(${primaryColorRGB}, 1)`" />
        <stop offset="50%" :stop-color="`rgba(${primaryColorRGB}, 0.5)`" />
        <stop offset="100%" :stop-color="`rgba(${primaryColorRGB}, 0)`" />
      </radialGradient>
    </defs>
    
    <!-- 
      使用 v-for 渲染当前所有正在飞行的流星。
      每个流星都是一个<path>元素。
    -->
    <path
      v-for="meteor in activeMeteors"
      :key="meteor.id"
      :d="meteor.pathData"
      :stroke="`url(#${gradientId})`"
      stroke-width="3"
      stroke-linecap="round"
      fill="none"
      class="meteor-path"
      @animationend="removeMeteor(meteor.id)"
    />
  </svg>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

// 定义流星的数据结构
interface Meteor {
  id: number;
  pathData: string; // SVG路径的 "d" 属性
}
interface Point {
  x: number;
  y: number;
}

// ================== State ==================
const activeMeteors = ref<Meteor[]>([]);
let meteorIdCounter = 0;

// 为了在SVG渐变中使用CSS变量，我们需要一些辅助计算
// 这里假设我们的主题色是 #e6c069
const primaryColorRGB = '230, 192, 105'; 
const gradientId = 'meteor-gradient-aurora';

// ================== Actions (暴露给父组件调用) ==================

/**
 * 【核心发射方法】
 * 从一个起点坐标，向一个或多个终点坐标发射流星。
 * @param start - 起点坐标 { x: number, y: number }
 * @param endPoints - 终点坐标数组 [{ x: number, y: number }]
 */
function fire(start: { x: number; y: number }, endPoints: { x: number; y: number }[]) {
  if (!start || !endPoints || endPoints.length === 0) return;

  endPoints.forEach((end, index) => {
    // 为每个目标点都创建一个流星，并加上一个小的延迟，让它们依次发射
    setTimeout(() => {
      // 使用二次贝塞尔曲线创建一条优雅的弧线
      // 控制点 (control point) 的位置决定了弧线的弯曲程度
      const controlX = (start.x + end.x) / 2 + (Math.random() - 0.5) * 200;
      const controlY = (start.y + end.y) / 2 - (Math.random() * 50 + 50);
      const pathData = `M ${start.x} ${start.y} Q ${controlX} ${controlY} ${end.x} ${end.y}`;
      
      activeMeteors.value.push({
        id: meteorIdCounter++,
        pathData: pathData,
      });
    }, index * 150); // 每颗流星间隔150毫秒发射
  });
}

/**
 * 当CSS动画结束后，从数组中移除该流星，避免DOM无限增长。
 * 这是通过 @animationend 事件自动触发的。
 */
function removeMeteor(id: number) {
  activeMeteors.value = activeMeteors.value.filter(m => m.id !== id);
}

// 使用 defineExpose 将 fire 方法暴露出去，这样父组件才能通过 ref 调用它
defineExpose({ fire });
</script>

<style lang="scss" scoped>
.meteor-svg-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  /* 关键：让鼠标可以穿透这个SVG层，点击到下面的元素 */
  pointer-events: none;
  z-index: 9998; /* 比加载动画低，比普通内容高 */
  overflow: hidden;
}

.meteor-path {
  /* 
    这是实现拖尾效果的核心魔法。
    我们使用 stroke-dasharray 和 stroke-dashoffset 的组合动画。
    想象一下，路径是一条长长的虚线，其中：
    - 实线部分是流星的“头部”，长度为100。
    - 空白部分是流星的“尾巴”，长度为900。
    总长度为1000。
    
    动画过程就是将这条虚线从头走到尾。
  */
  stroke-dasharray: 100 900;
  stroke-dashoffset: 1000;
  
  /* 应用动画 */
  /* forwards: 动画结束后保持在最后一帧的状态 */
  animation: shoot-meteor 1.8s cubic-bezier(0.5, 0, 0.2, 1) forwards;
}

@keyframes shoot-meteor {
  from {
    /* 动画开始时，虚线在路径的起点之外 */
    stroke-dashoffset: 1000;
  }
  to {
    /* 动画结束时，虚线移动到了路径的终点之外，完成了飞越 */
    stroke-dashoffset: -1000;
  }
}
</style>