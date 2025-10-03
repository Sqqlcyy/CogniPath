<template>
    <transition name="fade">
      <div v-if="isActive" class="loading-screen">
        <div class="galaxy-container">
          <div class="stars"></div>
          <div class="twinkling"></div>
          <div class="clouds"></div>
          <div class="nebula"></div>
        </div>
        <div class="status-text">
          <p>{{ status.text }}</p>
          <div class="progress-bar-wrapper">
            <div class="progress-bar" :style="{ width: `${status.progress}%` }"></div>
          </div>
        </div>
      </div>
    </transition>
  </template>
  
  <script setup lang="ts">
  defineProps<{ isActive: boolean; status: { text: string; progress: number } }>();
  </script>
  
  <style lang="scss">
/* /src/components/common/LoadingScreen.vue 的 <style> 部分 */

// --- 动画容器与布局 ---
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: #000;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  z-index: 9999;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.5s ease-in-out, visibility 0.5s ease-in-out;
  
  &.is-active {
    opacity: 1;
    visibility: visible;
  }
}

// --- 状态文本与进度条 ---
.status-text {
  color: #E5B84B; /* 主题金 */
  font-size: 20px;
  font-weight: 300;
  text-shadow: 0 0 10px rgba(229, 184, 75, 0.5);
  z-index: 10;
  margin-top: 250px; /* 放在动画下方 */
  text-align: center;
  letter-spacing: 1px;
  opacity: 0;
  animation: fadeInText 1.5s 1s ease-in-out forwards;
}

.progress-bar-wrapper {
  width: 300px;
  height: 4px;
  background-color: rgba(229, 184, 75, 0.1);
  border-radius: 2px;
  margin-top: 15px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #E5B84B, #FFC837);
  box-shadow: 0 0 10px #E5B84B;
  border-radius: 2px;
  transition: width 0.5s ease-out;
}

@keyframes fadeInText {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

// --- 核心：星系容器 ---
.galaxy-container {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  transform: translate(-50%, -50%);
}

// --- Layer 1: 最底层的静态小星星 ---
.stars {
  width: 1px;
  height: 1px;
  background: transparent;
  // 使用 box-shadow 生成大量随机分布的星星
  // 这里只写了100颗，你可以用SASS循环生成上千颗
  box-shadow: 
    -1440px 1030px #FFF, 48px -1352px #FFF, 1422px 1438px #FFF, 
    -1296px -1124px #FFF, 296px 972px #FFF, -1438px -1258px #FFF, 
    114px 1024px #FFF, -1214px 282px #FFF, 1064px -1446px #FFF, 
    -782px -858px #FFF, -944px 10px #FFF, 246px 632px #FFF, 
    1442px 792px #FFF, -822px -1064px #FFF, -108px -506px #FFF, 
    124px -1386px #FFF, 888px -1218px #FFF, 546px 690px #FFF, 
    -1300px -1072px #FFF, -1286px -862px #FFF, -118px 388px #FFF, 
    1434px -482px #FFF, -648px 30px #FFF, -108px -1438px #FFF, 
    -1200px 920px #FFF, 1404px 512px #FFF, -342px -1254px #FFF, 
    -1302px -1364px #FFF, 1264px -454px #FFF, -1458px 1002px #FFF, 
    -1358px 906px #FFF, -354px 1276px #FFF, -106px -1262px #FFF, 
    852px -1404px #FFF, 1374px 1358px #FFF, 1074px 308px #FFF, 
    -1402px 1324px #FFF, 584px -1268px #FFF, 218px -1106px #FFF, 
    804px 1198px #FFF, -1376px 1478px #FFF, -1078px -1004px #FFF, 
    126px 112px #FFF, 628px 1322px #FFF, 1384px -1490px #FFF, 
    -752px -1382px #FFF, -1336px 368px #FFF, -1412px -558px #FFF, 
    1112px 1290px #FFF, 1148px -1258px #FFF, -1304px -402px #FFF, 
    -664px 342px #FFF, 610px -1110px #FFF, -1124px -1186px #FFF, 
    110px 1018px #FFF, 756px -1220px #FFF, -1486px 878px #FFF, 
    1028px 1000px #FFF, -884px 998px #FFF, -1460px 428px #FFF, 
    -762px 1328px #FFF, 526px 648px #FFF, 1014px -1418px #FFF, 
    -1316px -1352px #FFF, -906px 1046px #FFF, 1214px 1092px #FFF, 
    -956px -1022px #FFF, -1232px -1334px #FFF, 1108px -516px #FFF, 
    -1294px 572px #FFF, 24px -1468px #FFF, -1140px -396px #FFF, 
    1258px -1014px #FFF, -1072px 1494px #FFF, 580px -1436px #FFF, 
    -790px 1344px #FFF, -1072px 426px #FFF, -1134px 944px #FFF, 
    -1218px 432px #FFF, 888px 1044px #FFF, -1110px -1350px #FFF, 
    -1378px 1242px #FFF, -1094px -1246px #FFF, -820px 406px #FFF, 
    1356px 1074px #FFF, -1376px -1314px #FFF, 1450px 1358px #FFF, 
    -1384px -1132px #FFF, 1374px 1466px #FFF, -1080px 1488px #FFF;
}

// --- Layer 2: 移动的、会闪烁的星星 (创建深度感) ---
.twinkling {
  width: 2000px;
  height: 100%;
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  background: transparent url('https://www.script-tutorials.com/demos/360/images/twinkling.png') repeat-y;
  background-size: 1000px 1000px;
  animation: move-twink-back 200s linear infinite;
}

// --- Layer 3: 移动的、模糊的云雾 (增加氛围感) ---
.clouds {
  width: 2000px;
  height: 100%;
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  background: transparent url('https://www.script-tutorials.com/demos/360/images/clouds.png') repeat-y;
  background-size: 1000px 1000px;
  animation: move-clouds-back 200s linear infinite;
}

// --- Layer 4: 核心视觉 - 旋转的星云 ---
.nebula {
  position: absolute;
  width: 400px;
  height: 400px;
  top: 50%;
  left: 50%;
  margin-left: -200px;
  margin-top: -200px;
  border-radius: 50%;
  
  // 使用伪元素创建多层、不同速度旋转的星云
  &::before, &::after {
    content: '';
    position: absolute;
    width: inherit;
    height: inherit;
    border-radius: 50%;
    animation: rotate 30s linear infinite;
  }
  
  // 内层星云
  &::before {
    background-image: radial-gradient(
      ellipse at center,
      rgba(255, 229, 180, 0.4) 0%,   /* 中心亮黄色 */
      rgba(255, 200, 55, 0.3) 30%,   /* 主题金 */
      rgba(255, 128, 8, 0.1) 60%,    /* 主题橙 */
      rgba(0, 0, 0, 0) 75%
    );
    transform: scale(0.8);
    filter: blur(10px);
    animation-duration: 25s; // 旋转速度稍快
  }
  
  // 外层星云
  &::after {
    background-image: radial-gradient(
      ellipse at center,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(230, 192, 105, 0.15) 40%,
      rgba(9, 10, 15, 0) 70%
    );
    filter: blur(5px);
    transform: scale(1.2);
    animation-direction: reverse; // 反向旋转
  }
  
  // 星云核心的脉冲光晕
  box-shadow: 0 0 50px -10px #E5B84B, 0 0 120px -20px #FFC837, 0 0 200px -30px #FF8008;
  animation: pulse-nebula 4s ease-in-out infinite alternate;
}

// --- 关键帧动画定义 ---

@keyframes move-twink-back {
  from { background-position: 0 0; }
  to { background-position: -10000px 5000px; }
}

@keyframes move-clouds-back {
  from { background-position: 0 0; }
  to { background-position: 10000px 0; }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse-nebula {
  0% {
    transform: scale(0.9);
    box-shadow: 0 0 50px -10px #E5B84B, 0 0 120px -20px #FFC837, 0 0 200px -30px #FF8008;
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 60px -5px #E5B84B, 0 0 140px -15px #FFC837, 0 0 250px -25px #FF8008;
    opacity: 1;
  }
}


/* 
  SASS 循环生成更多星星 (可选，如果想让星空更密集)
  你可以取消下面的注释来生成 700 颗星星
*/


@function random_range($min, $max) {
  $rand: random();
  $random_range: $min + floor($rand * ($max - $min + 1));
  @return $random_range;
}

.stars-more {
  width: 1px;
  height: 1px;
  background: transparent;
  $shadows: ();
  @for $i from 1 through 700 {
    $x: random_range(-2000, 2000) * 1px;
    $y: random_range(-2000, 2000) * 1px;
    $shadows: append($shadows, #{$x} #{$y} #FFF, comma);
  }
  box-shadow: $shadows;
}

  </style>