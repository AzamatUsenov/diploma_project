import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class LiveCodingScreen extends StatefulWidget {
  const LiveCodingScreen({super.key});

  @override
  State<LiveCodingScreen> createState() => _LiveCodingScreenState();
}

class _LiveCodingScreenState extends State<LiveCodingScreen> {
  final _inviteCodeController = TextEditingController();
  bool _loading = false;
  List<dynamic> _sessions = [];
  String? _role;

  @override
  void initState() {
    super.initState();
    _loadProfile();
    _loadSessions();
  }

  Future<void> _loadProfile() async {
    final profile = await ApiService.getStoredProfile();
    if (profile != null && mounted) {
      setState(() => _role = profile['role']);
    }
  }

  Future<void> _loadSessions() async {
    try {
      final data = await ApiService.get('/live/sessions/');
      if (mounted) {
        setState(() => _sessions = data['results'] ?? data['data'] ?? []);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка загрузки сессий: $e')),
        );
      }
    }
  }

  Future<void> _joinSession() async {
    final code = _inviteCodeController.text.trim().toUpperCase();
    if (code.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Введите код сессии')),
      );
      return;
    }

    setState(() => _loading = true);
    try {
      final session = await ApiService.post('/live/sessions/join/', body: {
        'invite_code': code,
      });
      if (mounted) {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => LiveSessionScreen(sessionId: session['id']),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: ${e is ApiException ? e.message : e}')),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _openCreateSession() {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => const _CreateSessionScreen()),
    ).then((_) => _loadSessions());
  }

  @override
  Widget build(BuildContext context) {
    final isHR = _role == 'hr';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Live Coding'),
      ),
      floatingActionButton: isHR
          ? FloatingActionButton.extended(
              onPressed: _openCreateSession,
              icon: const Icon(Icons.add),
              label: const Text('Создать сессию'),
            )
          : null,
      body: RefreshIndicator(
        onRefresh: _loadSessions,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (!isHR) ...[
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              color: Colors.green.shade50,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(Icons.flash_on, color: Colors.green.shade600),
                          ),
                          const SizedBox(width: 12),
                          const Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Присоединиться', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                                Text('Введите код от HR', style: TextStyle(fontSize: 13, color: Colors.grey)),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _inviteCodeController,
                        decoration: const InputDecoration(
                          labelText: 'Код приглашения',
                          hintText: 'ABCD1234',
                        ),
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontSize: 18, letterSpacing: 2, fontWeight: FontWeight.bold),
                        textCapitalization: TextCapitalization.characters,
                        maxLength: 8,
                      ),
                      const SizedBox(height: 8),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: _loading ? null : _joinSession,
                          child: _loading
                              ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                              : const Text('Войти в сессию'),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],

            if (_sessions.isNotEmpty) ...[
              Text(isHR ? 'Мои сессии' : 'Мои сессии',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              ..._sessions.map((s) => _sessionCard(s)),
            ] else if (!_loading) ...[
              const SizedBox(height: 32),
              Center(
                child: Column(
                  children: [
                    Icon(Icons.code_off, size: 48, color: Colors.grey.shade400),
                    const SizedBox(height: 12),
                    Text(
                      isHR ? 'Нет сессий. Создайте первую!' : 'Нет активных сессий',
                      style: TextStyle(color: Colors.grey.shade600),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _sessionCard(dynamic s) {
    final status = s['status'] ?? '';
    final isActive = status == 'waiting' || status == 'active';

    Color statusColor;
    String statusLabel;
    switch (status) {
      case 'waiting':
        statusColor = Colors.orange;
        statusLabel = 'Ожидание';
        break;
      case 'active':
        statusColor = Colors.green;
        statusLabel = 'Активна';
        break;
      case 'completed':
        statusColor = Colors.grey;
        statusLabel = 'Завершена';
        break;
      default:
        statusColor = Colors.red;
        statusLabel = 'Отменена';
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        title: Text(s['title'] ?? 'Без названия', style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: statusColor.withAlpha(25),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(statusLabel, style: TextStyle(fontSize: 11, color: statusColor, fontWeight: FontWeight.w600)),
            ),
            const SizedBox(width: 8),
            Text(s['invite_code'] ?? '', style: const TextStyle(fontFamily: 'monospace', fontWeight: FontWeight.bold)),
            const SizedBox(width: 8),
            Text('${s['time_limit_minutes'] ?? 30} мин', style: const TextStyle(fontSize: 12, color: Colors.grey)),
          ],
        ),
        trailing: isActive ? const Icon(Icons.chevron_right) : null,
        onTap: isActive
            ? () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => LiveSessionScreen(sessionId: s['id'])),
                )
            : null,
      ),
    );
  }

}

// ============ Create Session Screen ============

class _CreateSessionScreen extends StatefulWidget {
  const _CreateSessionScreen();

  @override
  State<_CreateSessionScreen> createState() => _CreateSessionScreenState();
}

class _CreateSessionScreenState extends State<_CreateSessionScreen> {
  final _titleCtrl = TextEditingController();
  int _timeLimit = 30;
  List<dynamic> _availableTasks = [];
  final Set<int> _selectedTaskIds = {};
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
          _availableTasks = tasks is List ? tasks : [];
          _loadingTasks = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _loadingTasks = false);
    }
  }

  Future<void> _create() async {
    if (_titleCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Введите название')),
      );
      return;
    }
    if (_selectedTaskIds.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Выберите хотя бы одну задачу')),
      );
      return;
    }

    setState(() => _creating = true);
    try {
      final session = await ApiService.post('/live/sessions/', body: {
        'title': _titleCtrl.text.trim(),
        'time_limit_minutes': _timeLimit,
        'question_ids': _selectedTaskIds.toList(),
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Сессия создана! Код: ${session['invite_code']}')),
        );
        Navigator.of(context).pop(session);
      }
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
      appBar: AppBar(title: const Text('Создать сессию')),
      body: _loadingTasks
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                TextField(
                  controller: _titleCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Название сессии',
                    hintText: 'Backend интервью — Python',
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    const Text('Время:', style: TextStyle(fontWeight: FontWeight.w600)),
                    const SizedBox(width: 12),
                    DropdownButton<int>(
                      value: _timeLimit,
                      items: [15, 20, 30, 45, 60, 90, 120]
                          .map((m) => DropdownMenuItem(value: m, child: Text('$m мин')))
                          .toList(),
                      onChanged: (v) => setState(() => _timeLimit = v ?? 30),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                const Text('Задачи:', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                if (_availableTasks.isEmpty)
                  const Text('Нет доступных code-задач. Запустите seed_data.',
                      style: TextStyle(color: Colors.grey))
                else
                  ..._availableTasks.map((task) {
                    final id = task['id'] as int;
                    final selected = _selectedTaskIds.contains(id);
                    return CheckboxListTile(
                      value: selected,
                      title: Text(
                        (task['text'] ?? '').toString().length > 60
                            ? '${(task['text']).toString().substring(0, 60)}...'
                            : task['text'] ?? '',
                        style: const TextStyle(fontSize: 14),
                      ),
                      subtitle: Text(task['language'] ?? '', style: const TextStyle(fontSize: 12)),
                      onChanged: (v) {
                        setState(() {
                          if (v == true) {
                            _selectedTaskIds.add(id);
                          } else {
                            _selectedTaskIds.remove(id);
                          }
                        });
                      },
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
                        : const Text('Создать сессию'),
                  ),
                ),
              ],
            ),
    );
  }
}

// ============ Live Session Screen ============

class LiveSessionScreen extends StatefulWidget {
  final String sessionId;
  const LiveSessionScreen({super.key, required this.sessionId});

  @override
  State<LiveSessionScreen> createState() => _LiveSessionScreenState();
}

class _LiveSessionScreenState extends State<LiveSessionScreen> {
  Map<String, dynamic>? _session;
  final _codeController = TextEditingController();
  int _currentTaskIndex = 0;
  bool _loading = true;
  bool _submitting = false;
  String? _role;

  WebSocketChannel? _wsChannel;
  Timer? _debounceTimer;
  bool _ignoreNextChange = false;

  @override
  void initState() {
    super.initState();
    _init();
  }

  @override
  void dispose() {
    _wsChannel?.sink.close();
    _debounceTimer?.cancel();
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _init() async {
    final profile = await ApiService.getStoredProfile();
    _role = profile?['role'];
    await _loadSession();
    _connectWebSocket();
    _codeController.addListener(_onCodeChanged);
  }

  void _onCodeChanged() {
    if (_ignoreNextChange || _role == 'hr') return;
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 200), () {
      _wsSend({'type': 'code_update', 'code': _codeController.text});
    });
  }

  Future<void> _connectWebSocket() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    if (token == null) return;

    const host = '10.0.2.2:8000';
    final uri = Uri.parse('ws://$host/ws/live/${widget.sessionId}/?token=$token');

    try {
      _wsChannel = WebSocketChannel.connect(uri);
      _wsChannel!.stream.listen(
        (message) => _handleWsMessage(message),
        onDone: () {},
        onError: (_) {},
      );
    } catch (_) {}
  }

  void _handleWsMessage(dynamic raw) {
    final data = jsonDecode(raw as String);
    final type = data['type'];

    if (type == 'code_update' && _role == 'hr') {
      _ignoreNextChange = true;
      _codeController.text = data['code'] ?? '';
      _codeController.selection = TextSelection.collapsed(offset: _codeController.text.length);
      _ignoreNextChange = false;
    } else if (type == 'switch_task') {
      final index = data['index'] ?? 0;
      if (mounted) {
        setState(() => _currentTaskIndex = index);
      }
    } else if (type == 'run_result') {
      if (mounted) {
        final passed = data['tests_passed'] ?? 0;
        final total = data['tests_total'] ?? 0;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Результат: $passed/$total тестов'),
            backgroundColor: data['status'] == 'passed' ? Colors.green : Colors.orange,
          ),
        );
      }
    } else if (type == 'extend_time') {
      if (mounted) {
        setState(() {
          _session?['time_limit_minutes'] = data['total_minutes'];
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('+${data['added']} мин (всего: ${data['total_minutes']} мин)')),
        );
      }
    } else if (type == 'chat_message') {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${data['sender']}: ${data['message']}')),
        );
      }
    } else if (type == 'session_state') {
      if (_role == 'hr' && data['code'] != null) {
        _ignoreNextChange = true;
        _codeController.text = data['code'];
        _ignoreNextChange = false;
      }
    }
  }

  void _wsSend(Map<String, dynamic> data) {
    if (_wsChannel != null) {
      _wsChannel!.sink.add(jsonEncode(data));
    }
  }

  Future<void> _loadSession() async {
    try {
      final data = await ApiService.get('/live/sessions/${widget.sessionId}/');
      if (mounted) {
        setState(() {
          _session = data;
          _loading = false;
          _currentTaskIndex = data['current_question_index'] ?? 0;
          if (data['questions'] != null && (data['questions'] as List).isNotEmpty) {
            _codeController.text = data['candidate_code'] ?? data['questions'][_currentTaskIndex]['code_template'] ?? '';
          }
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: ${e is ApiException ? e.message : e}')),
        );
        Navigator.of(context).pop();
      }
    }
  }

  Future<void> _submitTask() async {
    if (_session == null) return;
    final questions = _session!['questions'] as List?;
    if (questions == null || _currentTaskIndex >= questions.length) return;

    final questionId = questions[_currentTaskIndex]['id'];

    setState(() => _submitting = true);
    try {
      final result = await ApiService.post(
        '/live/sessions/${widget.sessionId}/submit-task/',
        body: {
          'question_id': questionId,
          'code': _codeController.text,
        },
      );

      _wsSend({
        'type': 'run_result',
        'status': result['status'],
        'tests_passed': result['tests_passed'] ?? 0,
        'tests_total': result['tests_total'] ?? 0,
        'output': result['output'] ?? '',
      });

      if (mounted) {
        final passed = result['tests_passed'] ?? 0;
        final total = result['tests_total'] ?? 0;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Результат: $passed/$total тестов'),
            backgroundColor: result['status'] == 'passed' ? Colors.green : Colors.orange,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: ${e is ApiException ? e.message : e}')),
        );
      }
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  Future<void> _extendTime() async {
    try {
      final result = await ApiService.post(
        '/live/sessions/${widget.sessionId}/extend-time/',
        body: {'minutes': 15},
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('+15 мин. Всего: ${result['time_limit_minutes']} мин')),
        );
        setState(() {
          _session!['time_limit_minutes'] = result['time_limit_minutes'];
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: ${e is ApiException ? e.message : e}')),
        );
      }
    }
  }

  Future<void> _endSession() async {
    try {
      await ApiService.post('/live/sessions/${widget.sessionId}/complete/');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Сессия завершена')),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: ${e is ApiException ? e.message : e}')),
        );
      }
    }
  }

  void _showShareDialog() {
    _showSendInviteSheet();
  }

  Future<void> _showSendInviteSheet() async {
    List<dynamic> applications = [];
    try {
      final data = await ApiService.get('/applications/');
      applications = data['results'] ?? [];
    } catch (_) {}

    if (!mounted) return;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.5,
        minChildSize: 0.3,
        maxChildSize: 0.8,
        expand: false,
        builder: (_, scrollCtrl) => Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  const Expanded(
                    child: Text('Отправить приглашение',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  ),
                  Text(
                    'Код: ${_session?['invite_code'] ?? ''}',
                    style: TextStyle(fontFamily: 'monospace', fontWeight: FontWeight.bold, color: Theme.of(context).colorScheme.primary),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            if (applications.isEmpty)
              const Expanded(
                child: Center(child: Text('Нет заявок для отправки', style: TextStyle(color: Colors.grey))),
              )
            else
              Expanded(
                child: ListView.builder(
                  controller: scrollCtrl,
                  itemCount: applications.length,
                  itemBuilder: (_, i) {
                    final app = applications[i];
                    return ListTile(
                      leading: CircleAvatar(
                        child: Text((app['applicant_username'] ?? 'U')[0].toUpperCase()),
                      ),
                      title: Text(app['applicant_username'] ?? 'Кандидат'),
                      subtitle: Text(app['job_title'] ?? ''),
                      trailing: FilledButton.tonal(
                        onPressed: () => _sendInviteToChat(app['id'], ctx),
                        child: const Text('Отправить'),
                      ),
                    );
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _sendInviteToChat(int applicationId, BuildContext sheetCtx) async {
    try {
      await ApiService.post(
        '/live/sessions/${widget.sessionId}/send-invite/',
        body: {'application_id': applicationId},
      );
      if (mounted) {
        Navigator.of(sheetCtx).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Приглашение отправлено в чат!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: ${e is ApiException ? e.message : e}')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading || _session == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Live Coding')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    final questions = _session!['questions'] as List? ?? [];
    final isHR = _role == 'hr';

    if (questions.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: const Text('Live Coding')),
        body: const Center(child: Text('Нет задач')),
      );
    }

    final currentTask = questions[_currentTaskIndex];

    return Scaffold(
      appBar: AppBar(
        title: Text(_session!['title'] ?? 'Live Coding'),
        actions: [
          if (isHR)
            IconButton(
              icon: const Icon(Icons.share),
              tooltip: 'Отправить в чат',
              onPressed: _showShareDialog,
            ),
          if (isHR)
            IconButton(
              icon: const Icon(Icons.more_time),
              tooltip: '+15 мин',
              onPressed: _extendTime,
            ),
          if (isHR)
            IconButton(
              icon: const Icon(Icons.stop_circle_outlined),
              tooltip: 'Завершить',
              onPressed: _endSession,
            ),
        ],
      ),
      body: Column(
        children: [
          // Session info bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: Theme.of(context).colorScheme.primaryContainer.withAlpha(80),
            child: Row(
              children: [
                Icon(Icons.timer, size: 16, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 4),
                Text('${_session!['time_limit_minutes']} мин',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.primary)),
                const SizedBox(width: 16),
                Icon(Icons.vpn_key, size: 16, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 4),
                Text(_session!['invite_code'] ?? '',
                    style: TextStyle(fontSize: 13, fontFamily: 'monospace', fontWeight: FontWeight.bold, color: Theme.of(context).colorScheme.primary)),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: _session!['status'] == 'active' ? Colors.green.shade100 : Colors.orange.shade100,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _session!['status'] == 'active' ? 'Live' : 'Ожидание',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: _session!['status'] == 'active' ? Colors.green.shade700 : Colors.orange.shade700,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Task tabs
          if (questions.length > 1)
            Container(
              height: 48,
              color: Theme.of(context).colorScheme.surfaceContainerHighest.withAlpha(80),
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: questions.length,
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                itemBuilder: (_, i) => Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text('Задача ${i + 1}'),
                    selected: i == _currentTaskIndex,
                    onSelected: (sel) {
                      if (sel) {
                        setState(() {
                          _currentTaskIndex = i;
                          _codeController.text = questions[i]['code_template'] ?? '';
                        });
                        if (_role != 'hr') {
                          _wsSend({'type': 'switch_task', 'index': i});
                        }
                      }
                    },
                  ),
                ),
              ),
            ),

          // Task description
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.secondaryContainer.withAlpha(60),
              border: Border(
                bottom: BorderSide(color: Theme.of(context).dividerColor.withAlpha(30)),
              ),
            ),
            child: Text(
              currentTask['text'] ?? 'Нет описания',
              style: const TextStyle(fontSize: 14),
            ),
          ),

          // Code editor
          Expanded(
            child: Container(
              color: Colors.grey.shade900,
              padding: const EdgeInsets.all(12),
              child: TextField(
                controller: _codeController,
                maxLines: null,
                expands: true,
                readOnly: isHR,
                style: const TextStyle(
                  fontFamily: 'Courier New',
                  fontSize: 13,
                  color: Colors.greenAccent,
                ),
                decoration: InputDecoration(
                  border: InputBorder.none,
                  hintText: isHR ? 'Код кандидата...' : '# Пишите код здесь...',
                  hintStyle: const TextStyle(color: Colors.grey),
                ),
              ),
            ),
          ),

          // Action bar
          if (!isHR)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                boxShadow: [
                  BoxShadow(color: Colors.black.withAlpha(10), blurRadius: 4, offset: const Offset(0, -2)),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _submitting ? null : _submitTask,
                      icon: _submitting
                          ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Icon(Icons.play_arrow),
                      label: const Text('Запустить'),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
