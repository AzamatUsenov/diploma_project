import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/common.dart';

class TestsScreen extends StatefulWidget {
  const TestsScreen({super.key});

  @override
  State<TestsScreen> createState() => _TestsScreenState();
}

class _TestsScreenState extends State<TestsScreen> {
  List<dynamic> _tests = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await ApiService.get('/tests/');
      setState(() {
        _tests = data['results'] ?? [];
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Тесты навыков', style: TextStyle(fontWeight: FontWeight.w700)),
        centerTitle: false,
      ),
      body: _loading
          ? ShimmerLoading.simpleCards()
          : _tests.isEmpty
              ? const EmptyState(
                  icon: Icons.quiz_outlined,
                  title: 'Нет доступных тестов',
                  subtitle: 'Тесты появятся здесь',
                )
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _tests.length,
                    itemBuilder: (ctx, i) => _testCard(_tests[i]),
                  ),
                ),
    );
  }

  Widget _testCard(Map<String, dynamic> test) {
    final difficulty = test['difficulty'] ?? 'junior';
    final diffConfig = {
      'junior': (Colors.green, 'Начальный'),
      'mid': (Colors.blue, 'Средний'),
      'senior': (Colors.purple, 'Продвинутый'),
    };
    final (color, label) = diffConfig[difficulty] ?? (Colors.grey, difficulty);
    final questionCount = test['question_count'] ?? test['questions_count'] ?? 0;

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        onTap: () => _startTest(test),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: color.withAlpha(25),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(Icons.code, color: color.shade700),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(test['title'] ?? '', style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        LevelBadge(difficulty),
                        const SizedBox(width: 8),
                        Text('$questionCount вопросов', style: TextStyle(fontSize: 12, color: Theme.of(context).hintColor)),
                      ],
                    ),
                  ],
                ),
              ),
              Icon(Icons.chevron_right, color: Theme.of(context).hintColor),
            ],
          ),
        ),
      ),
    );
  }

  void _startTest(Map<String, dynamic> test) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => _TestTakingScreen(testId: test['id'], title: test['title'] ?? 'Тест')),
    );
  }
}

class _TestTakingScreen extends StatefulWidget {
  final int testId;
  final String title;
  const _TestTakingScreen({required this.testId, required this.title});

  @override
  State<_TestTakingScreen> createState() => _TestTakingScreenState();
}

class _TestTakingScreenState extends State<_TestTakingScreen> {
  List<dynamic> _questions = [];
  Map<int, String> _answers = {};
  bool _loading = true;
  bool _submitting = false;
  Map<String, dynamic>? _result;

  @override
  void initState() {
    super.initState();
    _loadQuestions();
  }

  Future<void> _loadQuestions() async {
    try {
      final data = await ApiService.get('/tests/${widget.testId}/');
      setState(() {
        _questions = data['questions'] ?? [];
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Future<void> _submit() async {
    if (_answers.length < _questions.length) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ответьте на все вопросы')),
      );
      return;
    }
    setState(() => _submitting = true);
    try {
      final answers = _answers.entries.map((e) => {'question_id': e.key, 'answer': e.value}).toList();
      final result = await ApiService.post('/tests/${widget.testId}/submit/', body: {'answers': answers});
      setState(() {
        _result = result;
        _submitting = false;
      });
    } catch (e) {
      setState(() => _submitting = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Ошибка отправки')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.title, style: const TextStyle(fontWeight: FontWeight.w600))),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _result != null
              ? _resultView()
              : _questionsView(),
    );
  }

  Widget _resultView() {
    final score = _result!['score'] ?? 0;
    final maxScore = _result!['max_score'] ?? (_questions.length * 10);
    final percentage = _result!['percentage'] ?? (maxScore > 0 ? (score / maxScore * 100).round() : 0);
    final color = percentage >= 70 ? Colors.green : percentage >= 40 ? Colors.orange : Colors.red;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 120,
                  height: 120,
                  child: CircularProgressIndicator(
                    value: percentage / 100,
                    strokeWidth: 10,
                    backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest,
                    color: color,
                  ),
                ),
                Text('$percentage%', style: TextStyle(fontSize: 32, fontWeight: FontWeight.w800, color: color.shade700)),
              ],
            ),
            const SizedBox(height: 24),
            Text('$score из $maxScore баллов', style: TextStyle(fontSize: 16, color: Theme.of(context).hintColor)),
            const SizedBox(height: 8),
            Text(
              percentage >= 70 ? 'Отличный результат!' : percentage >= 40 ? 'Неплохо, но есть куда расти' : 'Стоит подучить материал',
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: color.shade700),
            ),
            const SizedBox(height: 32),
            FilledButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Вернуться к тестам'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _questionsView() {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Text('${_answers.length}/${_questions.length}', style: const TextStyle(fontWeight: FontWeight.w600)),
              const SizedBox(width: 12),
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: _questions.isEmpty ? 0 : _answers.length / _questions.length,
                    minHeight: 6,
                  ),
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: _questions.length,
            itemBuilder: (ctx, i) => _questionCard(i, _questions[i]),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(16),
          child: SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: _submitting ? null : _submit,
              child: _submitting
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Text('Завершить тест'),
            ),
          ),
        ),
      ],
    );
  }

  Widget _questionCard(int index, Map<String, dynamic> q) {
    final qId = q['id'] as int;
    final options = <String, String>{};
    if ((q['option_a'] ?? '').toString().isNotEmpty) options['a'] = q['option_a'];
    if ((q['option_b'] ?? '').toString().isNotEmpty) options['b'] = q['option_b'];
    if ((q['option_c'] ?? '').toString().isNotEmpty) options['c'] = q['option_c'];
    if ((q['option_d'] ?? '').toString().isNotEmpty) options['d'] = q['option_d'];

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('${index + 1}. ${q['text'] ?? ''}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
            const SizedBox(height: 12),
            ...options.entries.map((entry) {
              final key = entry.key;
              final text = entry.value;
              final selected = _answers[qId] == key;
              return Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: InkWell(
                  onTap: () => setState(() => _answers[qId] = key),
                  borderRadius: BorderRadius.circular(10),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: selected ? Theme.of(context).colorScheme.primaryContainer : Theme.of(context).colorScheme.surfaceContainerHighest.withAlpha(80),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: selected ? Theme.of(context).colorScheme.primary : Theme.of(context).colorScheme.outlineVariant,
                        width: selected ? 2 : 1,
                      ),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 28, height: 28,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: selected ? Theme.of(context).colorScheme.primary : Theme.of(context).colorScheme.surfaceContainerHighest,
                          ),
                          child: Center(
                            child: Text(
                              key.toUpperCase(),
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w700,
                                color: selected ? Theme.of(context).colorScheme.onPrimary : Theme.of(context).hintColor,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            text,
                            style: TextStyle(
                              fontSize: 13,
                              color: selected ? Theme.of(context).colorScheme.primary : Theme.of(context).colorScheme.onSurface,
                              fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}
