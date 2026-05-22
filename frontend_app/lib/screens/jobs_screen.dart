import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/common.dart';
import 'job_detail_screen.dart';
import 'compare_screen.dart';

Route _slideRoute(Widget page) {
  return PageRouteBuilder(
    pageBuilder: (context, animation, secondaryAnimation) => page,
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      return SlideTransition(
        position: Tween(begin: const Offset(1, 0), end: Offset.zero)
            .animate(CurvedAnimation(parent: animation, curve: Curves.easeOutCubic)),
        child: child,
      );
    },
    transitionDuration: const Duration(milliseconds: 300),
  );
}

class JobsScreen extends StatefulWidget {
  const JobsScreen({super.key});

  @override
  State<JobsScreen> createState() => _JobsScreenState();
}

class _JobsScreenState extends State<JobsScreen> {
  List<dynamic> _jobs = [];
  bool _loading = true;
  int _count = 0;
  String _search = '';
  String? _level;
  String _ordering = '-created_at';
  double _salaryMin = 0;
  double _salaryMax = 2500000;
  bool _salaryFilterActive = false;
  bool? _isRemote;
  bool? _trainingProvided;
  int _minHonesty = 0;
  final _searchCtrl = TextEditingController();

  bool _compareMode = false;
  final Set<int> _selectedIds = {};

  static const double _sliderMax = 2500000;

  @override
  void initState() {
    super.initState();
    _loadJobs();
  }

  Future<void> _loadJobs() async {
    setState(() => _loading = true);
    try {
      final query = <String, String>{
        'ordering': _ordering,
      };
      if (_search.isNotEmpty) query['search'] = _search;
      if (_level != null) query['level'] = _level!;
      if (_salaryFilterActive) {
        if (_salaryMin > 0) query['salary_min'] = _salaryMin.round().toString();
        if (_salaryMax < _sliderMax) query['salary_max'] = _salaryMax.round().toString();
      }
      if (_isRemote != null) query['is_remote'] = _isRemote.toString();
      if (_trainingProvided != null) query['training_provided'] = _trainingProvided.toString();
      if (_minHonesty > 0) query['min_honesty'] = _minHonesty.toString();

      final data = await ApiService.get('/jobs/', query: query);
      setState(() {
        _jobs = data['results'] ?? [];
        _count = data['count'] ?? 0;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  void _toggleCompareMode() {
    setState(() {
      _compareMode = !_compareMode;
      if (!_compareMode) _selectedIds.clear();
    });
  }

  void _toggleSelection(int id) {
    setState(() {
      if (_selectedIds.contains(id)) {
        _selectedIds.remove(id);
      } else if (_selectedIds.length < 4) {
        _selectedIds.add(id);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Максимум 4 вакансии для сравнения')),
        );
      }
    });
  }

  void _goCompare() {
    if (_selectedIds.length < 2) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Выберите минимум 2 вакансии')),
      );
      return;
    }
    Navigator.push(context, _slideRoute(CompareScreen(jobIds: _selectedIds.toList())));
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        title: Text(
          _compareMode ? 'Выберите вакансии (${_selectedIds.length}/4)' : 'Вакансии',
          style: const TextStyle(fontWeight: FontWeight.w700),
        ),
        centerTitle: false,
        actions: [
          IconButton(
            icon: Icon(_compareMode ? Icons.close : Icons.compare_arrows),
            tooltip: _compareMode ? 'Отмена' : 'Сравнить',
            onPressed: _toggleCompareMode,
          ),
          if (!_compareMode)
            IconButton(
              icon: const Icon(Icons.tune),
              onPressed: _showFilters,
            ),
        ],
      ),
      body: Column(
        children: [
          if (!_compareMode) ...[
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
              child: TextField(
                controller: _searchCtrl,
                decoration: InputDecoration(
                  hintText: 'Поиск вакансий...',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: _search.isNotEmpty
                      ? IconButton(icon: const Icon(Icons.close), onPressed: () {
                          _searchCtrl.clear();
                          _search = '';
                          _loadJobs();
                        })
                      : null,
                  filled: true,
                  fillColor: Theme.of(context).colorScheme.surfaceContainerHighest.withAlpha(80),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide.none),
                ),
                onSubmitted: (v) {
                  _search = v;
                  _loadJobs();
                },
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  Text('$_count вакансий', style: TextStyle(fontSize: 13, color: Theme.of(context).hintColor, fontWeight: FontWeight.w500)),
                  ..._activeFilterChips(cs),
                  const Spacer(),
                  ..._filterChips(),
                ],
              ),
            ),
          ],
          if (_compareMode)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              color: cs.primaryContainer.withAlpha(40),
              child: Row(
                children: [
                  Icon(Icons.info_outline, size: 16, color: cs.primary),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Выберите от 2 до 4 вакансий для сравнения',
                      style: TextStyle(fontSize: 13, color: cs.primary),
                    ),
                  ),
                ],
              ),
            ),
          Expanded(
            child: _loading
                ? ShimmerLoading.jobCards()
                : _jobs.isEmpty
                    ? const EmptyState(icon: Icons.search_off, title: 'Вакансии не найдены', subtitle: 'Попробуйте изменить фильтры')
                    : RefreshIndicator(
                        onRefresh: _loadJobs,
                        child: ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: _jobs.length,
                          itemBuilder: (ctx, i) => _jobCard(_jobs[i]),
                        ),
                      ),
          ),
        ],
      ),
      floatingActionButton: _compareMode && _selectedIds.length >= 2
          ? FloatingActionButton.extended(
              onPressed: _goCompare,
              icon: const Icon(Icons.compare_arrows),
              label: Text('Сравнить (${_selectedIds.length})'),
            )
          : null,
    );
  }

  bool get _hasActiveFilters => _salaryFilterActive || _isRemote != null || _trainingProvided != null || _minHonesty > 0;

  List<Widget> _activeFilterChips(ColorScheme cs) {
    final chips = <Widget>[];
    void addChip(String label, VoidCallback onClear) {
      chips.add(Padding(
        padding: const EdgeInsets.only(left: 6),
        child: GestureDetector(
          onTap: () { onClear(); _loadJobs(); },
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(color: cs.primary.withAlpha(25), borderRadius: BorderRadius.circular(8)),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Text(label, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: cs.primary)),
              const SizedBox(width: 4),
              Icon(Icons.close, size: 14, color: cs.primary),
            ]),
          ),
        ),
      ));
    }
    if (_salaryFilterActive) addChip('${_fmtSalary(_salaryMin)}-${_fmtSalary(_salaryMax)}', () => setState(() { _salaryFilterActive = false; _salaryMin = 0; _salaryMax = _sliderMax; }));
    if (_isRemote != null) addChip('Remote', () => setState(() => _isRemote = null));
    if (_trainingProvided != null) addChip('Обучение', () => setState(() => _trainingProvided = null));
    if (_minHonesty > 0) addChip('>${_minHonesty}%', () => setState(() => _minHonesty = 0));
    return chips;
  }

  String _fmtSalary(double n) {
    if (n >= 1000000) return '${(n / 1000000).toStringAsFixed(1)}M';
    return '${(n / 1000).round()}K';
  }

  List<Widget> _filterChips() {
    final levels = [null, 'junior', 'mid', 'senior'];
    final labels = ['Все', 'Junior', 'Mid', 'Senior'];
    return List.generate(levels.length, (i) {
      final selected = _level == levels[i];
      return Padding(
        padding: const EdgeInsets.only(left: 6),
        child: GestureDetector(
          onTap: () { setState(() => _level = levels[i]); _loadJobs(); },
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: selected ? Theme.of(context).colorScheme.primary : Theme.of(context).colorScheme.surfaceContainerHighest.withAlpha(80),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(labels[i], style: TextStyle(
              fontSize: 12, fontWeight: FontWeight.w600,
              color: selected ? Theme.of(context).colorScheme.onPrimary : Theme.of(context).hintColor,
            )),
          ),
        ),
      );
    });
  }

  Widget _jobCard(Map<String, dynamic> job) {
    final honesty = job['honesty_score'] ?? 100;
    final honestyColor = honesty >= 70 ? Colors.green : honesty >= 40 ? Colors.orange : Colors.red;
    final techStack = List<String>.from(job['tech_stack'] ?? []);
    final jobId = job['id'] as int;
    final isSelected = _selectedIds.contains(jobId);

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      shape: _compareMode && isSelected
          ? RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
              side: BorderSide(color: Theme.of(context).colorScheme.primary, width: 2),
            )
          : null,
      child: InkWell(
        onTap: _compareMode
            ? () => _toggleSelection(jobId)
            : () => Navigator.push(context, _slideRoute(JobDetailScreen(jobId: jobId))),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  if (_compareMode)
                    Padding(
                      padding: const EdgeInsets.only(right: 10),
                      child: Icon(
                        isSelected ? Icons.check_circle : Icons.radio_button_unchecked,
                        color: isSelected ? Theme.of(context).colorScheme.primary : Colors.grey,
                        size: 22,
                      ),
                    ),
                  Expanded(
                    child: Hero(
                      tag: 'job_title_$jobId',
                      child: Material(
                        color: Colors.transparent,
                        child: Text(job['title'] ?? '', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                      ),
                    ),
                  ),
                  LevelBadge(job['level'] ?? 'junior'),
                ],
              ),
              const SizedBox(height: 6),
              Row(
                children: [
                  Icon(Icons.business, size: 14, color: Theme.of(context).hintColor),
                  const SizedBox(width: 4),
                  Text(job['company'] ?? '', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: Theme.of(context).hintColor)),
                  const SizedBox(width: 12),
                  Icon(Icons.location_on_outlined, size: 14, color: Theme.of(context).hintColor),
                  const SizedBox(width: 4),
                  Flexible(child: Text(job['location'] ?? '', style: TextStyle(fontSize: 13, color: Theme.of(context).hintColor), overflow: TextOverflow.ellipsis)),
                  if (job['is_remote'] == true) ...[
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(color: Colors.indigo.withAlpha(25), borderRadius: BorderRadius.circular(6)),
                      child: const Text('Remote', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Colors.indigo)),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  SalaryText(min: job['salary_min'], max: job['salary_max']),
                  const SizedBox(width: 16),
                  Icon(Icons.verified, size: 14, color: honestyColor),
                  const SizedBox(width: 4),
                  Text('$honesty%', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: honestyColor)),
                  const SizedBox(width: 16),
                  Icon(Icons.schedule, size: 14, color: Theme.of(context).hintColor),
                  const SizedBox(width: 4),
                  Text('${job['experience_years'] ?? 0} лет', style: TextStyle(fontSize: 13, color: Theme.of(context).hintColor)),
                  if (job['training_provided'] == true) ...[
                    const SizedBox(width: 12),
                    Icon(Icons.school, size: 14, color: Colors.green.shade600),
                  ],
                ],
              ),
              if (techStack.isNotEmpty) ...[
                const SizedBox(height: 10),
                Wrap(
                  spacing: 6, runSpacing: 6,
                  children: techStack.take(6).map((t) => SkillChip(t)).toList(),
                ),
              ],
              if (job['is_overqualified'] == true) ...[
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(color: Colors.red.withAlpha(25), borderRadius: BorderRadius.circular(8)),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.warning_amber, size: 14, color: Colors.red.shade700),
                      const SizedBox(width: 4),
                      Text('Требования завышены', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Colors.red.shade700)),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  void _showFilters() {
    double tempMin = _salaryMin;
    double tempMax = _salaryMax;
    bool? tempRemote = _isRemote;
    bool? tempTraining = _trainingProvided;
    int tempHonesty = _minHonesty;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSheetState) => SingleChildScrollView(
          padding: EdgeInsets.fromLTRB(24, 24, 24, MediaQuery.of(ctx).viewInsets.bottom + 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Фильтры', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                  TextButton(
                    onPressed: () {
                      setSheetState(() {
                        tempMin = 0; tempMax = _sliderMax;
                        tempRemote = null; tempTraining = null; tempHonesty = 0;
                      });
                      setState(() => _ordering = '-created_at');
                    },
                    child: const Text('Сбросить'),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              const Text('Зарплата', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('от ${_fmtSalary(tempMin)} ₸', style: TextStyle(fontSize: 13, color: Theme.of(context).hintColor)),
                  Text('до ${_fmtSalary(tempMax)} ₸', style: TextStyle(fontSize: 13, color: Theme.of(context).hintColor)),
                ],
              ),
              RangeSlider(
                values: RangeValues(tempMin, tempMax),
                min: 0, max: _sliderMax, divisions: 50,
                labels: RangeLabels(_fmtSalary(tempMin), _fmtSalary(tempMax)),
                onChanged: (v) => setSheetState(() { tempMin = v.start; tempMax = v.end; }),
              ),
              const SizedBox(height: 12),

              const Text('Условия', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
              const SizedBox(height: 8),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Удалённая работа', style: TextStyle(fontSize: 14)),
                secondary: const Icon(Icons.home_work_outlined, size: 20),
                value: tempRemote == true,
                onChanged: (v) => setSheetState(() => tempRemote = v ? true : null),
              ),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Обучение предоставляется', style: TextStyle(fontSize: 14)),
                secondary: const Icon(Icons.school_outlined, size: 20),
                value: tempTraining == true,
                onChanged: (v) => setSheetState(() => tempTraining = v ? true : null),
              ),
              const SizedBox(height: 12),

              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Минимальная честность', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
                  Text('$tempHonesty%', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.primary)),
                ],
              ),
              Slider(
                value: tempHonesty.toDouble(),
                min: 0, max: 100, divisions: 20,
                label: '$tempHonesty%',
                onChanged: (v) => setSheetState(() => tempHonesty = v.round()),
              ),
              const SizedBox(height: 12),

              const Text('Сортировка', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
              const SizedBox(height: 4),
              ...[
                ('-created_at', 'Сначала новые'),
                ('-salary_max', 'По зарплате (больше)'),
                ('-honesty_score', 'По честности (выше)'),
                ('experience_years', 'По опыту (меньше)'),
              ].map((e) => RadioListTile<String>(
                title: Text(e.$2, style: const TextStyle(fontSize: 14)),
                value: e.$1, groupValue: _ordering, dense: true,
                onChanged: (v) { setState(() => _ordering = v!); setSheetState(() {}); },
              )),
              const SizedBox(height: 16),

              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: () {
                    setState(() {
                      _salaryMin = tempMin;
                      _salaryMax = tempMax;
                      _salaryFilterActive = tempMin > 0 || tempMax < _sliderMax;
                      _isRemote = tempRemote;
                      _trainingProvided = tempTraining;
                      _minHonesty = tempHonesty;
                    });
                    _loadJobs();
                    Navigator.pop(ctx);
                  },
                  child: const Text('Применить'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
