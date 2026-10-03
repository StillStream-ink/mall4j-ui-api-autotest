# Linux 运维文档

本项目用到的 Linux 命令与脚本。

---

## 一、环境健康检查

```bash
bash scripts/check_env.sh
```

检查项：

- 4 个端口（6379/8085/8086/9527）是否监听
- MySQL 是否连通、表数量
- Redis 是否连通、key 数量
- 磁盘使用率
- 内存占用

用到的命令：

- `netstat -tunlp` / `ss -tunlp` 查看端口监听
- `mysql -e "SELECT ..."` 数据库连通测试
- `redis-cli ping` 缓存连通测试
- `df -h` 磁盘
- `free -h` 内存

---

## 二、日志查看

```bash
# 实时查看 API 日志
bash scripts/tail_logs.sh api

# 只过滤 ERROR / Exception
bash scripts/tail_logs.sh error

# 按关键字过滤
bash scripts/tail_logs.sh grep "Order"

# 最近 50 条错误
bash scripts/tail_logs.sh last-error
```

用到的命令：

- `tail -f` 实时追踪
- `grep -E "ERROR|Exception"` 多模式匹配
- `grep --color=auto` 高亮
- `head` / `tail` 截取

---

## 三、测试数据清理

```bash
bash scripts/clean_test_data.sh
```

清理内容：

- MySQL：autotest_ 前缀的 config/role，au_ 前缀的 user
- Redis：*checkUserInputErrorPassword* 限流 key

用到的命令：

- `mysql <<EOF` 批量 SQL
- `redis-cli keys` + `redis-cli del`
- `while read` 遍历

---

## 四、批量测试 + 归档

```bash
bash scripts/batch_test.sh        # 全部
bash scripts/batch_test.sh api    # 只跑接口
bash scripts/batch_test.sh ui     # 只跑 UI
```

归档策略：每次跑完打包 `reports/archive/run_YYYYMMDD_HHMMSS.tar.gz`，自动清理 7 天前的归档。

用到的命令：

- `tar -czf` 打包压缩
- `find ... -mtime +7 -delete` 清理旧文件
- `date +%Y%m%d_%H%M%S` 时间戳

---

## 五、常用 Linux 命令速查

### 进程 / 端口

```bash
# 查看 Java 进程
ps aux | grep java
jps -l

# 查看端口占用
netstat -tunlp | grep 8085
lsof -i:8085

# 杀掉进程
kill -9 <PID>
```

### 日志

```bash
# 实时查看
tail -f /var/log/mall4j/api.log

# 查看最近 100 行
tail -100 api.log

# 过滤错误
grep -n "ERROR" api.log

# 统计错误数
grep -c "ERROR" api.log

# 时间范围
sed -n '/2026-10-02 10:00/,/2026-10-02 11:00/p' api.log

# 组合过滤
tail -f api.log | grep -E "ERROR|Exception" | grep -v "健康检查"
```

### 磁盘 / 内存

```bash
df -h          # 磁盘使用
du -sh *       # 当前目录各子项大小
du -sh /var/log/*  # 日志目录大小
free -h        # 内存
top            # 进程资源
```

### 文件

```bash
find . -name "*.log" -mtime +7        # 7 天前的日志
find . -name "*.log" -size +100M      # 大于 100M
gzip / gunzip                          # 压缩
tar -czf / tar -xzf                    # 打包
```

### 网络

```bash
ping 127.0.0.1
curl -v http://localhost:8085/doc.html
telnet 127.0.0.1 8085
```

### 系统信息

```bash
uname -a         # 内核
cat /etc/os-release  # 发行版
uptime           # 运行时长 + 负载
whoami           # 当前用户
```

---

## 六、部署流程（参考）

```bash
# 1. 检查环境
bash scripts/check_env.sh

# 2. 启动 4 个服务（后台运行）
nohup java -jar yami-shop-api.jar > logs/api.log 2>&1 &
nohup java -jar yami-shop-admin.jar > logs/admin.log 2>&1 &
nohup redis-server > logs/redis.log 2>&1 &

# 3. 查看启动状态
bash scripts/check_env.sh

# 4. 有问题时看日志
bash scripts/tail_logs.sh error

# 5. 跑测试
bash scripts/batch_test.sh all

# 6. 看报告
allure serve reports/allure-results
```
