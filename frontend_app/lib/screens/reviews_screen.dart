import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/common.dart';

class ReviewsScreen extends StatefulWidget {
  final String? companyName;
  const ReviewsScreen({this.companyName, super.key});

  @override
  State<ReviewsScreen> createState() => _ReviewsScreenState();
}

class _ReviewsScreenState extends State<ReviewsScreen> {
  List<dynamic> _reviews = [];
  Map<String, dynamic>? _stats;
  List<dynamic> _topCompanies = [];
  bool _loading = true;
  String? _filterCompany;

  @override
  void initState() {
    super.initState();
    _filterCompany = widget.companyName;
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final query = <String, String>{};
      if (_filterCompany != null && _filterCompany!.isNotEmpty) {
        query['company'] = _filterCompany!;
      }

      final reviewsData = await ApiService.get('/reviews/', query: query);
      final reviews = reviewsData['results'] ?? reviewsData['data'] ?? [];

      Map<String, dynamic>? stats;
      if (_filterCompany != null && _filterCompany!.isNotEmpty) {
        try {
          stats = await ApiService.get('/reviews/company-stats/', query: {'company': _filterCompany!});
        } catch (_) {}
      }

      List<dynamic> topCompanies = [];
      if (_filterCompany == null || _filterCompany!.isEmpty) {
        try {
          final topData = await ApiService.get('/reviews/top-companies/');
          topCompanies = topData['data'] ?? [];
        } catch (_) {}
      }

      setState(() {
        _reviews = reviews is List ? reviews : [];
        _stats = stats;
        _topCompanies = topCompanies is List ? topCompanies : [];
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        title: Text(
          _filterCompany != null ? 'Отзывы: $_filterCompany' : 'Отзывы о компаниях',
          style: const TextStyle(fontWeight: FontWeight.w700),
        ),
        centerTitle: false,
        actions: [
          if (_filterCompany != null)
            IconButton(
              icon: const Icon(Icons.clear),
              tooltip: 'Все компании',
              onPressed: () {
                setState(() {
                  _filterCompany = null;
                  _stats = null;
                });
                _load();
              },
            ),
        ],
      ),
      body: _loading
          ? ShimmerLoading.simpleCards()
          : RefreshIndicator(
              onRefresh: _load,
              child: CustomScrollView(
                slivers: [
                  if (_stats != null) SliverToBoxAdapter(child: _companyStatsCard(cs)),
                  if (_topCompanies.isNotEmpty && _filterCompany == null)
                    SliverToBoxAdapter(child: _topCompaniesSection(cs)),
                  if (_reviews.isEmpty)
                    const SliverFillRemaining(
                      child: EmptyState(
                        icon: Icons.rate_review_outlined,
                        title: 'Пока нет отзывов',
                        subtitle: 'Будьте первым — оставьте отзыв!',
                      ),
                    )
                  else
                    SliverPadding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      sliver: SliverList(
                        delegate: SliverChildBuilderDelegate(
                          (ctx, i) => _reviewCard(_reviews[i], cs),
                          childCount: _reviews.length,
                        ),
                      ),
                    ),
                  const SliverPadding(padding: EdgeInsets.only(bottom: 80)),
                ],
              ),
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showWriteReviewSheet(cs),
        icon: const Icon(Icons.edit),
        label: const Text('Написать отзыв'),
      ),
    );
  }

  Widget _companyStatsCard(ColorScheme cs) {
    final s = _stats!;
    final avg = (s['avg_total'] ?? 0).toDouble();
    final count = s['review_count'] ?? 0;

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.business, color: cs.primary),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      s['company_name'] ?? '',
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: _ratingColor(avg).withAlpha(25),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.star, size: 18, color: _ratingColor(avg)),
                        const SizedBox(width: 4),
                        Text(
                          avg.toStringAsFixed(1),
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: _ratingColor(avg)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text('$count отзывов', style: TextStyle(fontSize: 13, color: cs.onSurface.withAlpha(150))),
              const SizedBox(height: 16),
              _ratingBar('Общая оценка', (s['avg_overall'] ?? 0).toDouble()),
              _ratingBar('Work-Life баланс', (s['avg_work_life'] ?? 0).toDouble()),
              _ratingBar('Карьерный рост', (s['avg_career_growth'] ?? 0).toDouble()),
              _ratingBar('Зарплата', (s['avg_salary'] ?? 0).toDouble()),
              _ratingBar('Руководство', (s['avg_management'] ?? 0).toDouble()),
            ],
          ),
        ),
      ),
    );
  }

  Widget _ratingBar(String label, double value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          SizedBox(
            width: 130,
            child: Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
          ),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: value / 5,
                backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest,
                color: _ratingColor(value),
                minHeight: 8,
              ),
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 28,
            child: Text(
              value.toStringAsFixed(1),
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: _ratingColor(value)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _topCompaniesSection(ColorScheme cs) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Топ компаний', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          SizedBox(
            height: 100,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: _topCompanies.length,
              itemBuilder: (ctx, i) {
                final c = _topCompanies[i];
                final avg = (c['avg_total'] ?? 0).toDouble();
                return GestureDetector(
                  onTap: () {
                    setState(() => _filterCompany = c['company_name']);
                    _load();
                  },
                  child: Container(
                    width: 160,
                    margin: const EdgeInsets.only(right: 10),
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              c['company_name'] ?? '',
                              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 6),
                            Row(
                              children: [
                                ...List.generate(5, (si) => Icon(
                                  si < avg.round() ? Icons.star : Icons.star_border,
                                  size: 14,
                                  color: Colors.amber.shade700,
                                )),
                                const SizedBox(width: 4),
                                Text(avg.toStringAsFixed(1), style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '${c['review_count']} отзывов',
                              style: TextStyle(fontSize: 11, color: cs.onSurface.withAlpha(150)),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _reviewCard(Map<String, dynamic> review, ColorScheme cs) {
    final ratings = {
      'Общая': review['rating_overall'] ?? 0,
      'Баланс': review['rating_work_life'] ?? 0,
      'Рост': review['rating_career_growth'] ?? 0,
      'Зарплата': review['rating_salary'] ?? 0,
      'Руков.': review['rating_management'] ?? 0,
    };
    final avg = (review['average_rating'] ?? 0).toDouble();
    final isAnonymous = review['is_anonymous'] == true;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                CircleAvatar(
                  radius: 18,
                  backgroundColor: isAnonymous ? cs.surfaceContainerHighest : cs.primaryContainer,
                  child: Icon(
                    isAnonymous ? Icons.visibility_off : Icons.person,
                    size: 18,
                    color: isAnonymous ? cs.onSurface.withAlpha(150) : cs.primary,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        review['author_name'] ?? 'Аноним',
                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                      ),
                      if (review['position'] != null && review['position'].toString().isNotEmpty)
                        Text(
                          '${review['is_current_employee'] == true ? 'Работает' : 'Работал(а)'} — ${review['position']}',
                          style: TextStyle(fontSize: 12, color: cs.onSurface.withAlpha(150)),
                        ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _ratingColor(avg).withAlpha(25),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.star, size: 14, color: _ratingColor(avg)),
                      const SizedBox(width: 2),
                      Text(
                        avg.toStringAsFixed(1),
                        style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: _ratingColor(avg)),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            if (_filterCompany == null && review['company_name'] != null) ...[
              GestureDetector(
                onTap: () {
                  setState(() => _filterCompany = review['company_name']);
                  _load();
                },
                child: Row(
                  children: [
                    Icon(Icons.business, size: 14, color: cs.primary),
                    const SizedBox(width: 4),
                    Text(
                      review['company_name'],
                      style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: cs.primary),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
            ],

            Text(
              review['title'] ?? '',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 10),

            Wrap(
              spacing: 6, runSpacing: 6,
              children: ratings.entries.map((e) {
                final val = e.value is int ? e.value.toDouble() : (e.value as num).toDouble();
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _ratingColor(val).withAlpha(15),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('${e.key} ', style: TextStyle(fontSize: 11, color: Theme.of(context).hintColor)),
                      ...List.generate(5, (i) => Icon(
                        i < val.round() ? Icons.star : Icons.star_border,
                        size: 10,
                        color: _ratingColor(val),
                      )),
                    ],
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 12),

            _prosConsBlock(Icons.thumb_up_outlined, 'Плюсы', review['pros'] ?? '', Colors.green),
            const SizedBox(height: 8),
            _prosConsBlock(Icons.thumb_down_outlined, 'Минусы', review['cons'] ?? '', Colors.red),
            if (review['advice'] != null && review['advice'].toString().isNotEmpty) ...[
              const SizedBox(height: 8),
              _prosConsBlock(Icons.lightbulb_outline, 'Совет', review['advice'], Colors.amber.shade700),
            ],

            const SizedBox(height: 10),
            Row(
              children: [
                InkWell(
                  onTap: () => _toggleHelpful(review['id']),
                  borderRadius: BorderRadius.circular(8),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.thumb_up_alt_outlined, size: 16, color: cs.onSurface.withAlpha(150)),
                        const SizedBox(width: 4),
                        Text(
                          'Полезно (${review['helpful_count'] ?? 0})',
                          style: TextStyle(fontSize: 12, color: cs.onSurface.withAlpha(150)),
                        ),
                      ],
                    ),
                  ),
                ),
                const Spacer(),
                Text(
                  _formatDate(review['created_at']),
                  style: TextStyle(fontSize: 11, color: cs.onSurface.withAlpha(100)),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _prosConsBlock(IconData icon, String label, String text, Color color) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 6),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: color)),
              const SizedBox(height: 2),
              Text(text, style: TextStyle(fontSize: 13, color: Theme.of(context).colorScheme.onSurface.withAlpha(200), height: 1.4)),
            ],
          ),
        ),
      ],
    );
  }

  String _formatDate(String? iso) {
    if (iso == null) return '';
    final dt = DateTime.tryParse(iso);
    if (dt == null) return '';
    return '${dt.day.toString().padLeft(2, '0')}.${dt.month.toString().padLeft(2, '0')}.${dt.year}';
  }

  Color _ratingColor(double rating) {
    if (rating >= 4) return Colors.green;
    if (rating >= 3) return Colors.amber.shade700;
    if (rating >= 2) return Colors.orange;
    return Colors.red;
  }

  Future<void> _toggleHelpful(dynamic reviewId) async {
    try {
      final result = await ApiService.post('/reviews/$reviewId/helpful/');
      final idx = _reviews.indexWhere((r) => r['id'] == reviewId);
      if (idx >= 0 && mounted) {
        setState(() => _reviews[idx]['helpful_count'] = result['helpful_count']);
      }
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
      }
    }
  }

  void _showWriteReviewSheet(ColorScheme cs) {
    final companyCtrl = TextEditingController(text: _filterCompany ?? '');
    final titleCtrl = TextEditingController();
    final prosCtrl = TextEditingController();
    final consCtrl = TextEditingController();
    final adviceCtrl = TextEditingController();
    final positionCtrl = TextEditingController();
    bool isAnonymous = false;
    bool isCurrentEmployee = false;
    int ratingOverall = 0;
    int ratingWorkLife = 0;
    int ratingCareer = 0;
    int ratingSalary = 0;
    int ratingManagement = 0;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSheetState) {
          Widget starRow(String label, int value, ValueChanged<int> onChanged) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  SizedBox(
                    width: 120,
                    child: Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
                  ),
                  ...List.generate(5, (i) => GestureDetector(
                    onTap: () => setSheetState(() => onChanged(i + 1)),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 2),
                      child: Icon(
                        i < value ? Icons.star : Icons.star_border,
                        size: 28,
                        color: i < value ? Colors.amber.shade700 : Theme.of(context).hintColor,
                      ),
                    ),
                  )),
                ],
              ),
            );
          }

          return DraggableScrollableSheet(
            initialChildSize: 0.9,
            maxChildSize: 0.95,
            minChildSize: 0.5,
            expand: false,
            builder: (ctx, scrollCtrl) => SingleChildScrollView(
              controller: scrollCtrl,
              padding: EdgeInsets.fromLTRB(24, 24, 24, MediaQuery.of(ctx).viewInsets.bottom + 24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 40, height: 4,
                      decoration: BoxDecoration(color: Theme.of(context).colorScheme.outlineVariant, borderRadius: BorderRadius.circular(2)),
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text('Написать отзыв', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                  const SizedBox(height: 20),

                  TextField(
                    controller: companyCtrl,
                    decoration: const InputDecoration(labelText: 'Компания *', hintText: 'Название компании'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: titleCtrl,
                    decoration: const InputDecoration(labelText: 'Заголовок *', hintText: 'Кратко об опыте работы'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: positionCtrl,
                    decoration: const InputDecoration(labelText: 'Должность', hintText: 'Ваша позиция'),
                  ),
                  const SizedBox(height: 16),

                  const Text('Оценки', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 8),
                  starRow('Общая', ratingOverall, (v) => ratingOverall = v),
                  starRow('Work-Life', ratingWorkLife, (v) => ratingWorkLife = v),
                  starRow('Карьера', ratingCareer, (v) => ratingCareer = v),
                  starRow('Зарплата', ratingSalary, (v) => ratingSalary = v),
                  starRow('Руководство', ratingManagement, (v) => ratingManagement = v),
                  const SizedBox(height: 12),

                  TextField(
                    controller: prosCtrl,
                    decoration: const InputDecoration(labelText: 'Плюсы *', hintText: 'Что нравится в компании?'),
                    maxLines: 3,
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: consCtrl,
                    decoration: const InputDecoration(labelText: 'Минусы *', hintText: 'Что можно улучшить?'),
                    maxLines: 3,
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: adviceCtrl,
                    decoration: const InputDecoration(labelText: 'Совет руководству', hintText: 'Необязательно'),
                    maxLines: 2,
                  ),
                  const SizedBox(height: 12),

                  SwitchListTile(
                    contentPadding: EdgeInsets.zero,
                    title: const Text('Сейчас работаю здесь', style: TextStyle(fontSize: 14)),
                    value: isCurrentEmployee,
                    onChanged: (v) => setSheetState(() => isCurrentEmployee = v),
                  ),
                  SwitchListTile(
                    contentPadding: EdgeInsets.zero,
                    title: const Text('Анонимный отзыв', style: TextStyle(fontSize: 14)),
                    subtitle: const Text('Ваше имя не будет показано', style: TextStyle(fontSize: 12)),
                    value: isAnonymous,
                    onChanged: (v) => setSheetState(() => isAnonymous = v),
                  ),
                  const SizedBox(height: 16),

                  SizedBox(
                    width: double.infinity,
                    child: FilledButton(
                      onPressed: () async {
                        if (companyCtrl.text.isEmpty || titleCtrl.text.isEmpty ||
                            prosCtrl.text.isEmpty || consCtrl.text.isEmpty) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Заполните обязательные поля')),
                          );
                          return;
                        }
                        if (ratingOverall == 0 || ratingWorkLife == 0 || ratingCareer == 0 ||
                            ratingSalary == 0 || ratingManagement == 0) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Поставьте все оценки')),
                          );
                          return;
                        }
                        try {
                          await ApiService.post('/reviews/', body: {
                            'company_name': companyCtrl.text.trim(),
                            'title': titleCtrl.text.trim(),
                            'pros': prosCtrl.text.trim(),
                            'cons': consCtrl.text.trim(),
                            'advice': adviceCtrl.text.trim(),
                            'position': positionCtrl.text.trim(),
                            'rating_overall': ratingOverall,
                            'rating_work_life': ratingWorkLife,
                            'rating_career_growth': ratingCareer,
                            'rating_salary': ratingSalary,
                            'rating_management': ratingManagement,
                            'is_anonymous': isAnonymous,
                            'is_current_employee': isCurrentEmployee,
                          });
                          if (ctx.mounted) Navigator.pop(ctx);
                          if (mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Отзыв опубликован!')),
                            );
                            _load();
                          }
                        } on ApiException catch (e) {
                          if (mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text(e.message)),
                            );
                          }
                        }
                      },
                      child: const Text('Опубликовать'),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
