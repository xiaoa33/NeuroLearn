export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

export function formatTimeRemaining(nextReviewAt: string): string {
  const now = new Date();
  const next = new Date(nextReviewAt);
  const diffMs = next.getTime() - now.getTime();
  
  if (diffMs < 0) return '已到期';
  
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  
  if (days > 0) return `${days}天 ${hours}小时`;
  if (hours > 0) return `${hours}小时 ${mins}分钟`;
  return `${mins}分钟`;
}

export function getMemoryStrengthColor(strength: number): string {
  if (strength >= 0.7) return '#22c55e';
  if (strength >= 0.4) return '#eab308';
  return '#ef4444';
}

export function getMemoryStrengthLabel(strength: number): string {
  if (strength >= 0.8) return '牢固';
  if (strength >= 0.6) return '良好';
  if (strength >= 0.4) return '一般';
  if (strength >= 0.2) return '较弱';
  return '薄弱';
}

export function getDifficultyLabel(difficulty: number): string {
  const labels = ['', '基础', '理解', '应用'];
  return labels[difficulty] || '未知';
}

export function getDifficultyColor(difficulty: number): string {
  const colors = ['', '#22c55e', '#eab308', '#ef4444'];
  return colors[difficulty] || '#6b7280';
}

export function getStateLabel(state: string): string {
  const labels: Record<string, string> = {
    flow: '心流',
    anxiety: '焦虑',
    boredom: '无聊',
    confusion: '困惑',
    fatigue: '疲劳',
  };
  return labels[state] || state;
}

export function getStateColor(state: string): string {
  const colors: Record<string, string> = {
    flow: '#22c55e',
    anxiety: '#ef4444',
    boredom: '#eab308',
    confusion: '#a855f7',
    fatigue: '#6b7280',
  };
  return colors[state] || '#6b7280';
}

export function getChapterName(chapter: number): string {
  const names: Record<number, string> = {
    1: '绪论',
    2: '方法与技术',
    3: '细胞机制与认知',
    4: '神经解剖和发展',
    5: '感觉系统',
    6: '知觉',
    7: '物体识别',
    8: '学习与记忆',
    9: '运动控制',
    10: '情绪',
    11: '语言',
    12: '注意与意识',
  };
  return names[chapter] || `章节 ${chapter}`;
}

export function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}