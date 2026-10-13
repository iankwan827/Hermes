// 课堂笔记排版样式
// 来源：wechat_editor (https://github.com/littleben/wechat_editor)

const COURSE_NOTE_STYLES = {
  // 焦橙文档 - 暖色调，适合课堂笔记
  'warm-docs': {
    name: '焦橙文档',
    description: '暖橙色主题，米色背景引用块，清晰易读',
    styles: {
      container: 'max-width: 740px; margin: 0 auto; padding: 20px 24px 40px 24px; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; font-size: 16px; line-height: 1.8 !important; color: #1A1A1A !important; background-color: #FFFBF5 !important; word-wrap: break-word;',
      h1: 'font-size: 28px; font-weight: 700; color: #1A1A1A !important; line-height: 1.3 !important; margin: 36px 0 12px; padding-bottom: 12px; border-bottom: 3px solid #C2410C;',
      h2: 'font-size: 22px; font-weight: 700; color: #1A1A1A !important; line-height: 1.35 !important; margin: 36px 0 14px; padding-top: 16px; border-top: 3px solid #FB923C; padding-left: 12px; border-left: 4px solid #C2410C;',
      h3: 'font-size: 18px; font-weight: 600; color: #1A1A1A !important; line-height: 1.4 !important; margin: 28px 0 12px; padding-left: 10px; border-left: 3px solid #FB923C;',
      blockquote: 'margin: 20px 0; padding: 12px 18px; background-color: #FFF7ED !important; border-left: 4px solid #C2410C; color: #1A1A1A !important; font-size: 15px; line-height: 1.7 !important; border-radius: 0 8px 8px 0;',
      strong: 'font-weight: 700; color: #C2410C !important;',
      code: 'font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 14px; padding: 2px 6px; background-color: #FFF7ED !important; color: #C2410C !important; border-radius: 4px;',
      hr: 'margin: 32px 0; border: none; height: 2px; background: linear-gradient(to right, #C2410C, #FB923C, transparent);',
    }
  },

  // Apple极简 - 简洁大方
  'wechat-apple': {
    name: 'Apple极简',
    description: '苹果设计风格，无边框引用，居中排版',
    styles: {
      container: 'max-width: 680px; margin: 0 auto; padding: 20px 24px 40px 24px; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif; font-size: 17px; line-height: 1.7 !important; color: #86868b !important; background-color: #fff !important; word-wrap: break-word;',
      h1: 'font-size: 32px; font-weight: 600; color: #1d1d1f !important; line-height: 1.15 !important; margin: 36px 0 18px; letter-spacing: -0.015em;',
      h2: 'font-size: 26px; font-weight: 600; color: #1d1d1f !important; line-height: 1.2 !important; margin: 32px 0 16px; letter-spacing: -0.012em;',
      h3: 'font-size: 21px; font-weight: 600; color: #1d1d1f !important; line-height: 1.25 !important; margin: 28px 0 14px;',
      blockquote: 'margin: 24px auto; padding: 0; background-color: transparent !important; border-left: none; color: #1d1d1f !important; font-size: 18px; line-height: 1.45 !important; font-weight: 600; text-align: center; max-width: 560px; font-style: normal;',
      strong: 'font-weight: 600; color: #1d1d1f !important;',
      code: 'font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 14px; padding: 2px 6px; background-color: #f5f5f7 !important; color: #1d1d1f !important; border-radius: 4px;',
      hr: 'margin: 40px auto; border: none; height: 1px; background-color: #d2d2d7 !important; max-width: 80px;',
    }
  },

  // Jony Ive - 超极简
  'wechat-jonyive': {
    name: 'Jony Ive',
    description: '超细字体，极致留白，高端感',
    styles: {
      container: 'max-width: 680px; margin: 0 auto; padding: 24px 28px 48px 28px; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", sans-serif; font-size: 17px; line-height: 1.6 !important; color: #6e6e73 !important; background-color: #fff !important; word-wrap: break-word; font-weight: 300;',
      h1: 'font-size: 39px; font-weight: 200; color: #1d1d1f !important; line-height: 1.15 !important; margin: 48px 0 24px; letter-spacing: -0.025em;',
      h2: 'font-size: 28px; font-weight: 300; color: #1d1d1f !important; line-height: 1.2 !important; margin: 40px 0 20px; letter-spacing: -0.018em;',
      h3: 'font-size: 22px; font-weight: 300; color: #1d1d1f !important; line-height: 1.3 !important; margin: 32px 0 16px; letter-spacing: -0.01em;',
      blockquote: 'margin: 32px auto; padding: 0; background-color: transparent !important; border-left: none; color: #1d1d1f !important; font-size: 18px; line-height: 1.4 !important; font-weight: 300; text-align: center; max-width: 520px; font-style: normal;',
      strong: 'font-weight: 400; color: #1d1d1f !important;',
      code: 'font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 14px; padding: 2px 6px; background-color: #f5f5f7 !important; color: #1d1d1f !important; border-radius: 4px; font-weight: 300;',
      hr: 'margin: 48px auto; border: none; height: 1px; background-color: #d2d2d7 !important; max-width: 60px;',
    }
  },

  // 高迪有机 - 彩虹渐变，活泼
  'gaudi-organic': {
    name: '高迪有机',
    description: '彩虹渐变标题，有机曲线，活泼有趣',
    styles: {
      container: 'max-width: 720px; margin: 0 auto; padding: 20px 24px 40px 24px; font-family: "Georgia", "Noto Serif SC", "Source Han Serif SC", serif; font-size: 17px; line-height: 1.85 !important; color: #3d2914 !important; background-color: #FFFDF7 !important; word-wrap: break-word;',
      h1: 'font-size: 32px; font-weight: 700; color: #ff6b6b !important; background: linear-gradient(45deg, #ff6b6b, #ffd93d, #6bcf7f, #4ecdc4, #5b86e5, #a55eea); -webkit-background-clip: text; background-clip: text; line-height: 1.25 !important; margin: 36px 0 18px; text-align: center; letter-spacing: -0.02em; position: relative; padding: 12px;',
      h2: 'font-size: 26px; font-weight: 600; color: #c0392b !important; line-height: 1.3 !important; margin: 32px 0 16px; text-align: center; position: relative; padding-bottom: 12px;',
      h3: 'font-size: 21px; font-weight: 600; color: #e74c3c !important; line-height: 1.35 !important; margin: 28px 0 14px; padding-left: 16px; border-left: 4px solid #ff6b6b;',
      blockquote: 'margin: 20px auto; padding: 16px 22px; background: radial-gradient(circle at top left, rgba(255, 107, 107, 0.1) 0%, rgba(109, 207, 127, 0.1) 25%, rgba(78, 205, 196, 0.1) 50%, rgba(91, 134, 229, 0.1) 75%, rgba(165, 94, 234, 0.1) 100%); border: 3px solid transparent; border-image: linear-gradient(45deg, #ff6b6b, #ffd93d, #6bcf7f, #4ecdc4, #5b86e5, #a55eea) 1; border-radius: 50% 20% / 10% 40%; color: #3d2914 !important; font-size: 17px; line-height: 1.6 !important; font-style: italic; text-align: center; max-width: 600px;',
      strong: 'font-weight: 700; color: #c0392b !important; background-color: rgba(192, 57, 43, 0.08) !important; padding: 2px 6px; border-radius: 4px;',
      code: 'font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 14px; padding: 2px 8px; background: linear-gradient(135deg, rgba(255,107,107,0.1), rgba(78,205,196,0.1)); color: #c0392b !important; border-radius: 12px;',
      hr: 'margin: 36px auto; border: none; height: 3px; background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcf7f, #4ecdc4, #5b86e5, #a55eea); border-radius: 2px; max-width: 120px;',
    }
  }
};
