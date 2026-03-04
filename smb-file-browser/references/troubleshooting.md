# 故障排查指南

## 1. Clash Verge Fake-IP DNS 劫持

**症状**: DNS 解析返回 198.18.0.x，SMB 连接超时或 "socket was closed"。

**原因**: Clash Verge TUN 模式拦截所有 DNS（`dns-hijack: any:53`），返回 fake-ip。公共 DNS 查不到 `HT-FILE2.vipkid.work`（NXDOMAIN），但 fake-ip 仍分配假 IP。

**诊断**:
```bash
ifconfig | grep "198.18.0"        # 存在 utun 接口则 TUN 模式活跃
dig HT-FILE2.vipkid.work +short   # 返回 198.18.0.x 则被劫持
ipconfig getpacket en0             # 获取 DHCP 分配的企业 DNS
```

**解决**: `smb_connect.py` 自动处理，手动方式如下：

1. 修改 `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml`
2. 在 `dns:` 段添加 `fake-ip-filter: [+.vipkid.work]`
3. 添加 `nameserver-policy: {'+.vipkid.work': ['172.24.101.3', '172.24.101.2']}`
4. 通过 unix socket 重载：
   ```bash
   curl -s --unix-socket /tmp/verge/verge-mihomo.sock \
     -X PUT 'http://localhost/configs?force=true' \
     -H 'Content-Type: application/json' \
     -d '{"path":"<config_path>"}'
   ```

## 2. 认证失败

**症状**: `smbutil: server rejected the authentication`

**原因**: 用户名格式错误。SMB 认证使用 `panxiaoying`，不是 `panxiaoying@vipkid.com.cn`。

**解决**: 使用不含邮箱域名的用户名。密码中的 `@` 需要 URL 编码为 `%40`。

## 3. mount_smbfs 静默失败 (exit 1, 无输出)

**症状**: `mount_smbfs` 返回退出码 1，无任何错误信息。

**原因**: 挂载点目录已被占用或不干净。

**解决**:
```bash
umount /tmp/smb_mounts/DMFile 2>/dev/null
rmdir /tmp/smb_mounts/DMFile
mkdir -p /tmp/smb_mounts/DMFile
mount_smbfs -o nobrowse '//user:pass@ip/share' /tmp/smb_mounts/DMFile
```

## 4. 大文件下载中断

**症状**: 复制大文件时网络中断。

**解决**: 使用 `smb_download.py`，支持 `.partial` 文件断点续传：
```bash
python3 smb_download.py /path/to/source ./local/ --bw-limit 5M
```
中断后重新运行同一命令即可自动续传。

## 5. Windows 系统连接

```cmd
net use Z: \\172.23.250.32\DMFile /user:panxiaoying "Password@2025" /persistent:no
dir "Z:\双师智学2026"
```

如果主机名无法解析，直接使用 IP 地址 `172.23.250.32`。
