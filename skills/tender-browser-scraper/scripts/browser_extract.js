// 使用OpenClaw browser工具直接抓取数据
const projects = [];

// 使用JavaScript提取项目列表
const extractProjects = () => {
  const items = document.querySelectorAll('li');
  const results = [];
  
  items.forEach(li => {
    const link = li.querySelector('a[href*="/xxhz/"]');
    if (link) {
      const title = link.textContent.trim();
      const url = link.href;
      
      // 提取日期
      const dateText = li.textContent;
      const dateMatch = dateText.match(/\d{4}-\d{2}-\d{2}/);
      const date = dateMatch ? dateMatch[0] : '';
      
      results.push({ title, url, date });
    }
  });
  
  return results;
};

// 返回提取函数
extractProjects;
