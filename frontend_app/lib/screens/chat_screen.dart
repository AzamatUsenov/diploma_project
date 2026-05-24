import 'package:flutter/material.dart';
import 'dart:async';
import '../services/api_service.dart';

class ChatScreen extends StatefulWidget {
  final int applicationId;
  final String title;
  const ChatScreen({required this.applicationId, required this.title, super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  List<dynamic> _messages = [];
  bool _loading = true;
  bool _sending = false;
  final _ctrl = TextEditingController();
  final _scrollCtrl = ScrollController();
  Timer? _pollTimer;
  String? _myUsername;
  String? _role;

  @override
  void initState() {
    super.initState();
    _loadProfile();
    _loadMessages();
    _pollTimer = Timer.periodic(const Duration(seconds: 5), (_) => _loadMessages(silent: true));
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _ctrl.dispose();
    _scrollCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadProfile() async {
    final p = await ApiService.getStoredProfile();
    if (mounted) {
      setState(() {
        _myUsername = p?['username'];
        _role = p?['role'];
      });
    }
  }

  Future<void> _loadMessages({bool silent = false}) async {
    try {
      final data = await ApiService.get('/applications/${widget.applicationId}/messages/');
      if (mounted) {
        final list = data is List ? data : (data['results'] ?? data['data'] ?? []);
        setState(() {
          _messages = list is List ? list : [];
          if (!silent) _loading = false;
        });
        if (!silent) _scrollToBottom();
      }
    } catch (e) {
      if (mounted && !silent) setState(() => _loading = false);
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(_scrollCtrl.position.maxScrollExtent,
            duration: const Duration(milliseconds: 200), curve: Curves.easeOut);
      }
    });
  }

  Future<void> _send() async {
    final text = _ctrl.text.trim();
    if (text.isEmpty || _sending) return;

    setState(() => _sending = true);
    try {
      await ApiService.post('/applications/${widget.applicationId}/send/', body: {'text': text});
      _ctrl.clear();
      await _loadMessages(silent: true);
      _scrollToBottom();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Ошибка отправки')));
      }
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  void _showLiveCodingOptions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text('Live Coding', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            ),
            ListTile(
              leading: const Icon(Icons.add_circle_outline),
              title: const Text('Создать и отправить'),
              subtitle: const Text('Создать новую сессию и пригласить'),
              onTap: () {
                Navigator.pop(ctx);
                _createAndSendInvite();
              },
            ),
            ListTile(
              leading: const Icon(Icons.send),
              title: const Text('Отправить из существующих'),
              subtitle: const Text('Выбрать из ожидающих сессий'),
              onTap: () {
                Navigator.pop(ctx);
                _sendFromExisting();
              },
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  Future<void> _createAndSendInvite() async {
    final session = await Navigator.of(context).push<Map<String, dynamic>>(
      MaterialPageRoute(builder: (_) => const _CreateAndSendScreen()),
    );
    if (session != null && mounted) {
      try {
        await ApiService.post(
          '/live/sessions/${session['id']}/send-invite/',
          body: {'application_id': widget.applicationId},
        );
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Приглашение отправлено!')),
        );
        _loadMessages(silent: true);
        _scrollToBottom();
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: ${e is ApiException ? e.message : e}')),
        );
      }
    }
  }

  Future<void> _sendFromExisting() async {
    try {
      final data = await ApiService.get('/live/sessions/');
      final sessions = (data['results'] ?? data['data'] ?? []) as List;
      final waiting = sessions.where((s) => s['status'] == 'waiting').toList();

      if (!mounted) return;

      if (waiting.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Нет ожидающих сессий. Создайте новую.')),
        );
        return;
      }

      showModalBottomSheet(
        context: context,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        builder: (ctx) => SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Padding(
                padding: EdgeInsets.all(16),
                child: Text('Выберите сессию', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
              ...waiting.map((s) => ListTile(
                    title: Text(s['title'] ?? 'Без названия'),
                    subtitle: Text('Код: ${s['invite_code']} · ${s['time_limit_minutes']} мин'),
                    trailing: FilledButton.tonal(
                      onPressed: () async {
                        Navigator.pop(ctx);
                        try {
                          await ApiService.post(
                            '/live/sessions/${s['id']}/send-invite/',
                            body: {'application_id': widget.applicationId},
                          );
                          if (mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Приглашение отправлено!')),
                            );
                            _loadMessages(silent: true);
                            _scrollToBottom();
                          }
                        } catch (e) {
                          if (mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('Ошибка: ${e is ApiException ? e.message : e}')),
                            );
                          }
                        }
                      },
                      child: const Text('Отправить'),
                    ),
                  )),
              const SizedBox(height: 8),
            ],
          ),
        ),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка загрузки сессий: ${e is ApiException ? e.message : e}')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title, style: const TextStyle(fontWeight: FontWeight.w600)),
        actions: [
          if (_role == 'hr')
            IconButton(
              icon: const Icon(Icons.code),
              tooltip: 'Live Coding',
              onPressed: _showLiveCodingOptions,
            ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _messages.isEmpty
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(32),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.chat_bubble_outline, size: 64, color: Theme.of(context).hintColor.withAlpha(100)),
                              const SizedBox(height: 16),
                              Text('Нет сообщений', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Theme.of(context).hintColor)),
                              const SizedBox(height: 8),
                              Text('Начните диалог!', style: TextStyle(fontSize: 13, color: Theme.of(context).hintColor.withAlpha(150))),
                            ],
                          ),
                        ),
                      )
                    : ListView.builder(
                        controller: _scrollCtrl,
                        padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                        itemCount: _messages.length,
                        itemBuilder: (ctx, i) => _messageBubble(_messages[i]),
                      ),
          ),
          _inputBar(cs),
        ],
      ),
    );
  }

  Widget _messageBubble(dynamic msg) {
    final isMe = msg['sender_username'] == _myUsername;
    final role = msg['sender_role'] ?? '';
    final text = msg['text'] ?? '';
    final time = msg['created_at'] ?? '';
    final timeStr = time.length >= 16 ? time.substring(11, 16) : '';
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Align(
      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: isMe
              ? Theme.of(context).colorScheme.primary
              : isDark ? Colors.grey.shade800 : Colors.grey.shade100,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isMe ? 16 : 4),
            bottomRight: Radius.circular(isMe ? 4 : 16),
          ),
        ),
        child: Column(
          crossAxisAlignment: isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            if (!isMe)
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  '${msg['sender_username']} · ${role == 'hr' ? 'HR' : 'Соискатель'}',
                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: isDark ? Colors.grey.shade300 : Colors.grey.shade600),
                ),
              ),
            Text(text, style: TextStyle(fontSize: 14, color: isMe ? Colors.white : Theme.of(context).colorScheme.onSurface)),
            const SizedBox(height: 4),
            Text(timeStr, style: TextStyle(fontSize: 10, color: isMe ? Colors.white70 : Theme.of(context).hintColor)),
          ],
        ),
      ),
    );
  }

  Widget _inputBar(ColorScheme cs) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      padding: EdgeInsets.fromLTRB(16, 8, 8, 8 + MediaQuery.of(context).padding.bottom),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        boxShadow: [BoxShadow(color: Colors.black.withAlpha(8), blurRadius: 8, offset: const Offset(0, -2))],
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _ctrl,
              decoration: InputDecoration(
                hintText: 'Сообщение...',
                filled: true,
                fillColor: isDark ? Colors.grey.shade800 : Colors.grey.shade100,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(24), borderSide: BorderSide.none),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              ),
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _send(),
            ),
          ),
          const SizedBox(width: 8),
          IconButton.filled(
            onPressed: _sending ? null : _send,
            icon: _sending
                ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Icon(Icons.send, size: 20),
          ),
        ],
      ),
    );
  }
}

// ============ Create session from chat ============

class _CreateAndSendScreen extends StatefulWidget {
  const _CreateAndSendScreen();

  @override
  State<_CreateAndSendScreen> createState() => _CreateAndSendScreenState();
}

class _CreateAndSendScreenState extends State<_CreateAndSendScreen> {
  final _titleCtrl = TextEditingController();
  int _timeLimit = 30;
  List<dynamic> _tasks = [];
  final Set<int> _selected = {};
  bool _loadingTasks = true;
  bool _creating = false;

  @override
  void initState() {
    super.initState();
    _loadTasks();
  }

  Future<void> _loadTasks() async {
    try {
      final data = await ApiService.get('/live/sessions/available-tasks/');
      final tasks = data['data'] ?? data;
      if (mounted) {
        setState(() {
          _tasks = tasks is List ? tasks : [];
          _loadingTasks = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _loadingTasks = false);
    }
  }

  Future<void> _create() async {
    if (_titleCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Введите название')));
      return;
    }
    if (_selected.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Выберите задачи')));
      return;
    }

    setState(() => _creating = true);
    try {
      final session = await ApiService.post('/live/sessions/', body: {
        'title': _titleCtrl.text.trim(),
        'time_limit_minutes': _timeLimit,
        'question_ids': _selected.toList(),
      });
      if (mounted) Navigator.of(context).pop(session);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: ${e is ApiException ? e.message : e}')),
        );
      }
    } finally {
      if (mounted) setState(() => _creating = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Создать Live Coding')),
      body: _loadingTasks
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                TextField(
                  controller: _titleCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Название',
                    hintText: 'Backend интервью',
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    const Text('Время:', style: TextStyle(fontWeight: FontWeight.w600)),
                    const SizedBox(width: 12),
                    DropdownButton<int>(
                      value: _timeLimit,
                      items: [15, 20, 30, 45, 60, 90]
                          .map((m) => DropdownMenuItem(value: m, child: Text('$m мин')))
                          .toList(),
                      onChanged: (v) => setState(() => _timeLimit = v ?? 30),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                const Text('Задачи:', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                if (_tasks.isEmpty)
                  const Text('Нет code-задач', style: TextStyle(color: Colors.grey))
                else
                  ..._tasks.map((t) {
                    final id = t['id'] as int;
                    return CheckboxListTile(
                      value: _selected.contains(id),
                      title: Text(
                        (t['text'] ?? '').toString().length > 55
                            ? '${t['text'].toString().substring(0, 55)}...'
                            : t['text'] ?? '',
                        style: const TextStyle(fontSize: 14),
                      ),
                      subtitle: Text(t['language'] ?? '', style: const TextStyle(fontSize: 12)),
                      onChanged: (v) => setState(() {
                        v == true ? _selected.add(id) : _selected.remove(id);
                      }),
                      controlAffinity: ListTileControlAffinity.leading,
                      dense: true,
                    );
                  }),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: FilledButton(
                    onPressed: _creating ? null : _create,
                    child: _creating
                        ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                        : const Text('Создать и отправить'),
                  ),
                ),
              ],
            ),
    );
  }
}
