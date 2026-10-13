# Session 超时与重启的保存流程

## _session_expiry_watcher (run.py:5628)

每 300 秒（5分钟）执行一次：

```
while self._running:
    for key, entry in session_store._entries:
        if entry.expiry_finalized: continue
        if not _is_session_expired(entry): continue
        expired_entries.append((key, entry))
    
    for key, entry in expired_entries:
        # 1. 触发 hook（agent 还在）
        invoke_hook("on_session_finalize", session_id=..., platform=..., reason="session_expired")
        
        # 2. 获取 cached agent
        _cached_agent = _agent_cache.get(key)
        
        # 3. 【已加入】保存对话
        self._auto_save_session(_cached_agent)
        
        # 4. 清理 agent 资源
        self._cleanup_agent_resources(_cached_agent)
        
        # 5. 从缓存移除
        self._evict_cached_agent(key)
        
        # 6. 标记完成
        entry.expiry_finalized = True
```

## _stop_impl (run.py:6038) — restart/shutdown 时

```
_stop_impl():
    _running = False
    _draining = True
    
    # 1. 通知所有活跃 session
    await _notify_active_sessions_of_shutdown()
    
    # 2. drain 活跃 agent（等它们完成或超时）
    active_agents, timed_out = await _drain_active_agents(timeout)
    
    # 3. 发起 detached restart（如果需要）
    if restart_detached: await _launch_detached_restart_command()
    
    # 4.【已加入】保存活跃 agent 对话
    _finalize_shutdown_agents(active_agents)
    
    # 5.【已加入】保存 idle agent 对话
    for _entry in _idle_agents:
        self._auto_save_session(_agent)
        self._cleanup_agent_resources(_agent)
    
    # 6. 断开 adapters
    for platform, adapter in self.adapters:
        await adapter.disconnect()
    
    # 7. 清理
    self._running_agents.clear()
    
    # 8. 退出（让 service manager 重启）
    exit(75)  # GATEWAY_SERVICE_RESTART_EXIT_CODE
```

## _is_session_expired (session.py:785)

```python
def _is_session_expired(self, entry):
    policy = self.config.get_reset_policy(platform=entry.platform, session_type=entry.chat_type)
    
    if policy.mode == "none": return False
    
    now = _now()
    
    # idle 模式：最后更新时间 + idle_minutes < now
    if policy.mode in {"idle", "both"}:
        if now > entry.updated_at + timedelta(minutes=policy.idle_minutes):
            return True
    
    # daily 模式：最后更新时间 < 今天的重置时间
    if policy.mode in {"daily", "both"}:
        today_reset = now.replace(hour=policy.at_hour, minute=0)
        if now.hour < policy.at_hour:
            today_reset -= timedelta(days=1)
        if entry.updated_at < today_reset:
            return True
    
    return False
```
