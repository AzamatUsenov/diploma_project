import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/common.dart';
import 'job_detail_screen.dart';

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
  final _searchCtrl = TextEditingController();

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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Вакансии', style: TextStyle(fontWeight: FontWeight.w700)),
        centerTitle: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.tune),
            onPressed: _showFilters,
          ),
        ],
      ),
      body: Column(
        children: [
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
                fillColor: Colors.grey.shade100,
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
                Text('$_count вакансий', style: TextStyle(fontSize: 13, color: Colors.grey.shade600, fontWeight: FontWeight.w500)),
                if (_salaryFilterActive) ...[
                  const SizedBox(width: 8),
                  GestureDetector(
                    onTap: () {
                      setState(() {
                        _salaryFilterActive = false;
                        _salaryMin = 0;
                        _salaryMax = _sliderMax;
                      });
                      _loadJobs();
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.indigo.withAlpha(25),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text('${_fmtSalary(_salaryMin)} – ${_fmtSalary(_salaryMax)}',
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Colors.indigo)),
                          const SizedBox(width: 4),
                          const Icon(Icons.close, size: 14, color: Colors.indigo),
                        ],
                      ),
                    ),
                  ),
                ],
                const Spacer(),
                ..._filterChips(),
              ],
            ),
          ),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
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
    );
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
              color: selected ? Theme.of(context).colorScheme.primary : Colors.grey.shade100,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(labels[i], style: TextStyle(
              fontSize: 12, fontWeight: FontWeight.w600,
              color: selected ? Colors.white : Colors.grey.shade700,
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

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        onTap: () => Navigator.push(context, MaterialPageRoute(
          builder: (_) => JobDetailScreen(jobId: job['id']),
        )),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(job['title'] ?? '', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                  ),
                  LevelBadge(job['level'] ?? 'junior'),
                ],
              ),
              const SizedBox(height: 6),
              Row(
                children: [
                  Icon(Icons.business, size: 14, color: Colors.grey.shade500),
                  const SizedBox(width: 4),
                  Text(job['company'] ?? '', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: Colors.grey.shade700)),
                  const SizedBox(width: 12),
                  Icon(Icons.location_on_outlined, size: 14, color: Colors.grey.shade500),
                  const SizedBox(width: 4),
                  Flexible(child: Text(job['location'] ?? '', style: TextStyle(fontSize: 13, color: Colors.grey.shade600), overflow: TextOverflow.ellipsis)),
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
                  Icon(Icons.schedule, size: 14, color: Colors.grey.shade500),
                  const SizedBox(width: 4),
                  Text('${job['experience_years'] ?? 0} лет', style: TextStyle(fontSize: 13, color: Colors.grey.shade600)),
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

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSheetState) => Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Фильтры', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
              const SizedBox(height: 20),

              // Salary range
              const Text('Зарплата', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('от ${_fmtSalary(tempMin)} ₸', style: TextStyle(fontSize: 13, color: Colors.grey.shade600)),
                  Text('до ${_fmtSalary(tempMax)} ₸', style: TextStyle(fontSize: 13, color: Colors.grey.shade600)),
                ],
              ),
              RangeSlider(
                values: RangeValues(tempMin, tempMax),
                min: 0,
                max: _sliderMax,
                divisions: 50,
                labels: RangeLabels(_fmtSalary(tempMin), _fmtSalary(tempMax)),
                onChanged: (v) {
                  setSheetState(() {
                    tempMin = v.start;
                    tempMax = v.end;
                  });
                },
              ),
              const SizedBox(height: 16),

              // Sorting
              const Text('Сортировка', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              const SizedBox(height: 8),
              ...[
                ('-created_at', 'Сначала новые'),
                ('-salary_max', 'По зарплате (больше)'),
                ('-honesty_score', 'По честности (выше)'),
                ('experience_years', 'По опыту (меньше)'),
              ].map((e) => RadioListTile<String>(
                title: Text(e.$2, style: const TextStyle(fontSize: 14)),
                value: e.$1,
                groupValue: _ordering,
                dense: true,
                onChanged: (v) {
                  setState(() => _ordering = v!);
                  setSheetState(() {});
                },
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
