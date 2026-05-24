import 'package:flutter/material.dart';
import '../services/api_service.dart';

class CodeChallengeScreen extends StatefulWidget {
  final int testId;
  final String title;
  const CodeChallengeScreen({super.key, required this.testId, required this.title});

  @override
  State<CodeChallengeScreen> createState() => _CodeChallengeScreenState();
}

class _CodeChallengeScreenState extends State<CodeChallengeScreen> {
  List<dynamic> _questions = [];
  bool _loading = true;
  int _currentIndex = 0;
  Map<int, Map<String, dynamic>> _progress = {};

  @override
  void initState() {
    super.initState();
    _loadQuestions();
  }

  Future<void> _loadQuestions() async {
    try {
      final data = await ApiService.get('/tests/${widget.testId}/');
      final questions = (data['questions'] as List?)?.where((q) => q['question_type'] == 'code').toList() ?? [];
      setState(() {
        _questions = questions;
        _loading = false;
      });
      _loadProgress();
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Future<void> _loadProgress() async {
    try {
      final data = await ApiService.get('/tests/code/progress/${widget.testId}/');
      final tasks = data['tasks'] as List? ?? [];
      setState(() {
        for (final t in tasks) {
          _progress[t['question_id']] = t;
        }
      });
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title, style: const TextStyle(fontWeight: FontWeight.w600)),
        bottom: _questions.length > 1
            ? PreferredSize(
                preferredSize: const Size.fromHeight(40),
                child: _taskTabs(),
              )
            : null,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _questions.isEmpty
              ? const Center(child: Text('Нет задач для кодинга'))
              : _CodeTaskView(
                  key: ValueKey(_questions[_currentIndex]['id']),
                  question: _questions[_currentIndex],
                  index: _currentIndex,
                  total: _questions.length,
                  onSolved: () => _loadProgress(),
                ),
    );
  }

  Widget _taskTabs() {
    return SizedBox(
      height: 40,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        itemCount: _questions.length,
        itemBuilder: (ctx, i) {
          final selected = i == _currentIndex;
          final qId = _questions[i]['id'] as int;
          final solved = _progress[qId]?['solved'] == true;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              avatar: solved ? const Icon(Icons.check_circle, size: 16, color: Colors.green) : null,
              label: Text('Задача ${i + 1}'),
              selected: selected,
              onSelected: (_) => setState(() => _currentIndex = i),
            ),
          );
        },
      ),
    );
  }
}

class _CodeTaskView extends StatefulWidget {
  final Map<String, dynamic> question;
  final int index;
  final int total;
  final VoidCallback? onSolved;
  const _CodeTaskView({super.key, required this.question, required this.index, required this.total, this.onSolved});

  @override
  State<_CodeTaskView> createState() => _CodeTaskViewState();
}

class _CodeTaskViewState extends State<_CodeTaskView> {
  late TextEditingController _codeController;
  bool _submitting = false;
  Map<String, dynamic>? _result;
  bool _showDescription = true;

  @override
  void initState() {
    super.initState();
    _codeController = TextEditingController(text: widget.question['code_template'] ?? '');
  }

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _runCode() async {
    setState(() {
      _submitting = true;
      _result = null;
    });

    try {
      final questionId = widget.question['id'];
      final result = await ApiService.post(
        '/tests/code/submit/$questionId/',
        body: {'code': _codeController.text},
      );
      setState(() {
        _result = result;
        _submitting = false;
      });
      if (result['status'] == 'passed') {
        widget.onSolved?.call();
      }
    } catch (e) {
      setState(() {
        _submitting = false;
        _result = {
          'status': 'error',
          'error_message': 'Ошибка отправки: $e',
          'test_results': [],
          'tests_passed': 0,
          'tests_total': 0,
        };
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final visibleTests = widget.question['visible_tests'] as List?;

    return Column(
      children: [
        if (_showDescription) _descriptionPanel(theme, visibleTests),
        _toggleBar(theme),
        Expanded(child: _codeEditor(theme)),
        if (_result != null) _resultsPanel(theme),
        _bottomBar(theme),
      ],
    );
  }

  Widget _descriptionPanel(ThemeData theme, List? visibleTests) {
    return Container(
      width: double.infinity,
      constraints: const BoxConstraints(maxHeight: 200),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withAlpha(60),
        border: Border(bottom: BorderSide(color: theme.dividerColor)),
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Задача ${widget.index + 1} из ${widget.total}',
              style: TextStyle(fontSize: 12, color: theme.hintColor, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 6),
            Text(
              widget.question['text'] ?? '',
              style: const TextStyle(fontSize: 14, height: 1.5),
            ),
            if (visibleTests != null && visibleTests.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text('Тесты:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: theme.hintColor)),
              const SizedBox(height: 4),
              ...visibleTests.map((t) => Padding(
                padding: const EdgeInsets.only(bottom: 2),
                child: Row(
                  children: [
                    Icon(Icons.check_circle_outline, size: 14, color: theme.hintColor),
                    const SizedBox(width: 6),
                    Text(t.toString(), style: TextStyle(fontSize: 12, color: theme.hintColor)),
                  ],
                ),
              )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _toggleBar(ThemeData theme) {
    return InkWell(
      onTap: () => setState(() => _showDescription = !_showDescription),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 4),
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerHighest.withAlpha(40),
          border: Border(bottom: BorderSide(color: theme.dividerColor)),
        ),
        child: Icon(
          _showDescription ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
          size: 18,
          color: theme.hintColor,
        ),
      ),
    );
  }

  Widget _codeEditor(ThemeData theme) {
    return Container(
      color: theme.brightness == Brightness.dark
          ? const Color(0xFF1E1E1E)
          : const Color(0xFFF8F9FA),
      child: TextField(
        controller: _codeController,
        maxLines: null,
        expands: true,
        textAlignVertical: TextAlignVertical.top,
        style: TextStyle(
          fontFamily: 'monospace',
          fontSize: 13,
          height: 1.5,
          color: theme.brightness == Brightness.dark ? Colors.white : Colors.black87,
        ),
        decoration: InputDecoration(
          contentPadding: const EdgeInsets.all(14),
          border: InputBorder.none,
          hintText: '// Напишите код здесь...',
          hintStyle: TextStyle(color: theme.hintColor.withAlpha(100)),
        ),
        keyboardType: TextInputType.multiline,
      ),
    );
  }

  Widget _resultsPanel(ThemeData theme) {
    final status = _result!['status'] ?? 'error';
    final testResults = (_result!['test_results'] as List?) ?? [];
    final passed = _result!['tests_passed'] ?? 0;
    final total = _result!['tests_total'] ?? 0;
    final errorMessage = _result!['error_message'] ?? '';
    final execTime = _result!['execution_time_ms'] ?? 0;

    final isError = status == 'error' || status == 'timeout';
    final allPassed = status == 'passed';
    final statusColor = allPassed ? Colors.green : isError ? Colors.red : Colors.orange;

    return Container(
      constraints: const BoxConstraints(maxHeight: 250),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withAlpha(80),
        border: Border(top: BorderSide(color: statusColor.withAlpha(100), width: 2)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            color: statusColor.withAlpha(20),
            child: Row(
              children: [
                Icon(
                  allPassed ? Icons.check_circle : isError ? Icons.error : Icons.warning,
                  size: 18,
                  color: statusColor,
                ),
                const SizedBox(width: 8),
                Text(
                  allPassed
                      ? 'Все тесты пройдены!'
                      : isError
                          ? (status == 'timeout' ? 'Превышено время выполнения' : 'Ошибка выполнения')
                          : 'Тесты: $passed / $total',
                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: statusColor),
                ),
                const Spacer(),
                Text('${execTime}ms', style: TextStyle(fontSize: 11, color: theme.hintColor)),
              ],
            ),
          ),
          if (isError && errorMessage.isNotEmpty)
            Flexible(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(12),
                child: SizedBox(
                  width: double.infinity,
                  child: Text(
                    errorMessage,
                    style: TextStyle(fontFamily: 'monospace', fontSize: 12, color: Colors.red.shade300),
                  ),
                ),
              ),
            ),
          if (!isError && testResults.isNotEmpty)
            Flexible(
              child: ListView.builder(
                shrinkWrap: true,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                itemCount: testResults.length,
                itemBuilder: (ctx, i) {
                  final test = testResults[i];
                  final testPassed = test['passed'] == true;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(
                          testPassed ? Icons.check_circle : Icons.cancel,
                          size: 16,
                          color: testPassed ? Colors.green : Colors.red,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                test['name'] ?? 'Test ${i + 1}',
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  color: testPassed ? Colors.green : Colors.red,
                                ),
                              ),
                              if (!testPassed && (test['message'] ?? '').isNotEmpty)
                                Padding(
                                  padding: const EdgeInsets.only(top: 2),
                                  child: Text(
                                    test['message'],
                                    style: TextStyle(
                                      fontFamily: 'monospace',
                                      fontSize: 11,
                                      color: theme.hintColor,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
        ],
      ),
    );
  }

  Widget _bottomBar(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor,
        border: Border(top: BorderSide(color: theme.dividerColor)),
      ),
      child: Row(
        children: [
          if (_result != null)
            TextButton.icon(
              onPressed: () => setState(() => _result = null),
              icon: const Icon(Icons.close, size: 16),
              label: const Text('Скрыть'),
            ),
          const Spacer(),
          FilledButton.icon(
            onPressed: _submitting ? null : _runCode,
            icon: _submitting
                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Icon(Icons.play_arrow, size: 18),
            label: Text(_submitting ? 'Выполняется...' : 'Запустить код'),
          ),
        ],
      ),
    );
  }
}
