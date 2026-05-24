import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../widgets/common.dart' show ShimmerLoading;

class CalendarScreen extends StatefulWidget {
  const CalendarScreen({super.key});

  @override
  State<CalendarScreen> createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  List<dynamic> _upcoming = [];
  List<dynamic> _all = [];
  bool _loading = true;
  String? _role;
  DateTime _selectedMonth = DateTime.now();

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final profile = await ApiService.getStoredProfile();
      final upcomingData = await ApiService.get('/applications/interviews/upcoming/');
      final allData = await ApiService.get('/applications/interviews/');

      setState(() {
        _role = profile?['role'];
        _upcoming = upcomingData['data'] ?? (upcomingData.containsKey('results') ? upcomingData['results'] : []);
        final allRaw = allData['results'] ?? allData['data'] ?? [];
        _all = allRaw is List ? allRaw : [];
        if (_upcoming.isEmpty) {
          final raw = upcomingData.values.firstWhere((v) => v is List, orElse: () => []);
          if (raw is List) _upcoming = raw;
        }
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Map<DateTime, List<dynamic>> get _eventsByDate {
    final map = <DateTime, List<dynamic>>{};
    for (final interview in _all) {
      final raw = interview['scheduled_at'];
      if (raw == null) continue;
      final dt = DateTime.tryParse(raw);
      if (dt == null) continue;
      final key = DateTime(dt.year, dt.month, dt.day);
      map.putIfAbsent(key, () => []).add(interview);
    }
    return map;
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Календарь', style: TextStyle(fontWeight: FontWeight.w700)),
        centerTitle: false,
        actions: [
          if (_role == 'hr')
            IconButton(
              icon: const Icon(Icons.add_circle_outline),
              tooltip: 'Назначить собеседование',
              onPressed: _showScheduleDialog,
            ),
        ],
      ),
      body: _loading
          ? ShimmerLoading.jobCards()
          : RefreshIndicator(
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  _buildCalendar(cs),
                  const SizedBox(height: 24),
                  _buildUpcomingSection(cs),
                  const SizedBox(height: 24),
                  _buildAllSection(cs),
                ],
              ),
            ),
    );
  }

  Widget _buildCalendar(ColorScheme cs) {
    final now = DateTime.now();
    final firstDay = DateTime(_selectedMonth.year, _selectedMonth.month, 1);
    final lastDay = DateTime(_selectedMonth.year, _selectedMonth.month + 1, 0);
    final startWeekday = firstDay.weekday;
    final events = _eventsByDate;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                IconButton(
                  icon: const Icon(Icons.chevron_left),
                  onPressed: () => setState(() {
                    _selectedMonth = DateTime(_selectedMonth.year, _selectedMonth.month - 1);
                  }),
                ),
                Text(
                  DateFormat('LLLL yyyy', 'ru').format(_selectedMonth),
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                IconButton(
                  icon: const Icon(Icons.chevron_right),
                  onPressed: () => setState(() {
                    _selectedMonth = DateTime(_selectedMonth.year, _selectedMonth.month + 1);
                  }),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
                  .map((d) => Expanded(
                        child: Center(
                          child: Text(d, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cs.onSurfaceVariant)),
                        ),
                      ))
                  .toList(),
            ),
            const SizedBox(height: 4),
            ...List.generate(6, (week) {
              return Row(
                children: List.generate(7, (day) {
                  final dayNum = week * 7 + day - (startWeekday - 2);
                  if (dayNum < 1 || dayNum > lastDay.day) {
                    return const Expanded(child: SizedBox(height: 40));
                  }
                  final date = DateTime(_selectedMonth.year, _selectedMonth.month, dayNum);
                  final isToday = date.year == now.year && date.month == now.month && date.day == now.day;
                  final hasEvent = events.containsKey(date);

                  return Expanded(
                    child: GestureDetector(
                      onTap: hasEvent ? () => _showDayEvents(date, events[date]!) : null,
                      child: Container(
                        height: 40,
                        margin: const EdgeInsets.all(1),
                        decoration: BoxDecoration(
                          color: isToday ? cs.primary.withAlpha(30) : null,
                          borderRadius: BorderRadius.circular(8),
                          border: isToday ? Border.all(color: cs.primary, width: 1.5) : null,
                        ),
                        child: Stack(
                          alignment: Alignment.center,
                          children: [
                            Text(
                              '$dayNum',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: isToday ? FontWeight.w700 : FontWeight.w500,
                                color: isToday ? cs.primary : cs.onSurface,
                              ),
                            ),
                            if (hasEvent)
                              Positioned(
                                bottom: 4,
                                child: Container(
                                  width: 6,
                                  height: 6,
                                  decoration: BoxDecoration(
                                    color: cs.primary,
                                    shape: BoxShape.circle,
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                    ),
                  );
                }),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildUpcomingSection(ColorScheme cs) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.event, color: cs.primary, size: 20),
            const SizedBox(width: 8),
            const Text('Ближайшие', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
          ],
        ),
        const SizedBox(height: 12),
        if (_upcoming.isEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Center(
                child: Column(
                  children: [
                    Icon(Icons.event_available, size: 40, color: cs.onSurfaceVariant.withAlpha(100)),
                    const SizedBox(height: 8),
                    Text('Нет предстоящих собеседований', style: TextStyle(color: cs.onSurfaceVariant)),
                  ],
                ),
              ),
            ),
          )
        else
          ..._upcoming.map((i) => _interviewCard(i, highlight: true)),
      ],
    );
  }

  Widget _buildAllSection(ColorScheme cs) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Все собеседования', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
        const SizedBox(height: 12),
        if (_all.isEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Center(
                child: Text('Нет собеседований', style: TextStyle(color: cs.onSurfaceVariant)),
              ),
            ),
          )
        else
          ..._all.map((i) => _interviewCard(i, highlight: false)),
      ],
    );
  }

  Widget _interviewCard(Map<String, dynamic> interview, {bool highlight = false}) {
    final cs = Theme.of(context).colorScheme;
    final raw = interview['scheduled_at'] ?? '';
    final dt = DateTime.tryParse(raw);
    final time = dt != null ? DateFormat('HH:mm', 'ru').format(dt) : '';
    final status = interview['status'] ?? 'scheduled';
    final duration = interview['duration_minutes'] ?? 30;

    final statusConfig = {
      'scheduled': (cs.primary, 'Запланировано'),
      'confirmed': (Colors.green, 'Подтверждено'),
      'completed': (Colors.grey, 'Проведено'),
      'cancelled': (Colors.red, 'Отменено'),
    };
    final (color, label) = statusConfig[status] ?? (cs.primary, status);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      color: highlight ? cs.primary.withAlpha(12) : null,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: highlight ? cs.primary.withAlpha(60) : Theme.of(context).dividerColor,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: cs.primary.withAlpha(20),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    dt != null ? '${dt.day}' : '-',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: cs.primary),
                  ),
                  if (dt != null)
                    Text(
                      DateFormat('MMM', 'ru').format(dt),
                      style: TextStyle(fontSize: 10, color: cs.primary),
                    ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          interview['job_title'] ?? 'Собеседование',
                          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: color.withAlpha(25),
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: color.withAlpha(60)),
                        ),
                        child: Text(label, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: color)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '$time · $duration мин${_role == "hr" && interview["applicant_username"] != null ? " · ${interview["applicant_username"]}" : ""}',
                    style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant),
                  ),
                  if (interview['location'] != null && (interview['location'] as String).isNotEmpty) ...[
                    const SizedBox(height: 2),
                    Text(
                      interview['location'],
                      style: TextStyle(fontSize: 12, color: cs.primary),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ],
              ),
            ),
            if (status == 'scheduled' || status == 'confirmed')
              PopupMenuButton<String>(
                icon: Icon(Icons.more_vert, size: 20, color: cs.onSurfaceVariant),
                onSelected: (action) => _handleAction(interview['id'], action),
                itemBuilder: (_) => [
                  if (status == 'scheduled' && _role != 'hr')
                    const PopupMenuItem(value: 'confirm', child: Text('Подтвердить')),
                  const PopupMenuItem(value: 'cancel', child: Text('Отменить')),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _handleAction(int id, String action) async {
    final status = action == 'confirm' ? 'confirmed' : 'cancelled';
    try {
      await ApiService.patch('/applications/interviews/$id/status/', body: {'status': status});
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(action == 'confirm' ? 'Подтверждено' : 'Отменено')),
      );
      _load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Ошибка')));
      }
    }
  }

  void _showDayEvents(DateTime date, List<dynamic> events) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                DateFormat('d MMMM yyyy', 'ru').format(date),
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 16),
              ...events.map((e) => _interviewCard(e as Map<String, dynamic>)),
            ],
          ),
        );
      },
    );
  }

  void _showScheduleDialog() async {
    List<dynamic> applications = [];
    try {
      final data = await ApiService.get('/applications/');
      applications = (data['results'] ?? []) as List;
      applications = applications.where((a) => ['pending', 'reviewed', 'accepted'].contains(a['status'])).toList();
    } catch (_) {}

    if (!mounted) return;
    if (applications.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Нет подходящих заявок для назначения')),
      );
      return;
    }

    int? selectedAppId;
    DateTime? selectedDate;
    TimeOfDay? selectedTime;
    int duration = 30;
    final locationCtrl = TextEditingController();
    final notesCtrl = TextEditingController();

    await showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setDialogState) {
            return AlertDialog(
              title: const Text('Назначить собеседование'),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    DropdownButtonFormField<int>(
                      decoration: const InputDecoration(labelText: 'Кандидат'),
                      items: applications.map<DropdownMenuItem<int>>((a) {
                        return DropdownMenuItem(
                          value: a['id'] as int,
                          child: Text('${a["applicant_username"]} — ${a["job_title"]}', overflow: TextOverflow.ellipsis),
                        );
                      }).toList(),
                      onChanged: (v) => setDialogState(() => selectedAppId = v),
                    ),
                    const SizedBox(height: 12),
                    ListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(selectedDate != null
                          ? DateFormat('d MMMM yyyy', 'ru').format(selectedDate!)
                          : 'Выберите дату'),
                      trailing: const Icon(Icons.calendar_today),
                      onTap: () async {
                        final d = await showDatePicker(
                          context: ctx,
                          initialDate: DateTime.now().add(const Duration(days: 1)),
                          firstDate: DateTime.now(),
                          lastDate: DateTime.now().add(const Duration(days: 365)),
                          locale: const Locale('ru'),
                        );
                        if (d != null) setDialogState(() => selectedDate = d);
                      },
                    ),
                    ListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(selectedTime != null
                          ? selectedTime!.format(ctx)
                          : 'Выберите время'),
                      trailing: const Icon(Icons.access_time),
                      onTap: () async {
                        final t = await showTimePicker(
                          context: ctx,
                          initialTime: const TimeOfDay(hour: 10, minute: 0),
                        );
                        if (t != null) setDialogState(() => selectedTime = t);
                      },
                    ),
                    DropdownButtonFormField<int>(
                      decoration: const InputDecoration(labelText: 'Длительность'),
                      initialValue: duration,
                      items: [15, 30, 45, 60, 90]
                          .map((m) => DropdownMenuItem(value: m, child: Text('$m мин')))
                          .toList(),
                      onChanged: (v) => setDialogState(() => duration = v ?? 30),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: locationCtrl,
                      decoration: const InputDecoration(labelText: 'Место / ссылка'),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: notesCtrl,
                      decoration: const InputDecoration(labelText: 'Заметки'),
                      maxLines: 2,
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx),
                  child: const Text('Отмена'),
                ),
                FilledButton(
                  onPressed: () async {
                    if (selectedAppId == null || selectedDate == null || selectedTime == null) {
                      ScaffoldMessenger.of(ctx).showSnackBar(
                        const SnackBar(content: Text('Заполните все обязательные поля')),
                      );
                      return;
                    }
                    final scheduledAt = DateTime(
                      selectedDate!.year,
                      selectedDate!.month,
                      selectedDate!.day,
                      selectedTime!.hour,
                      selectedTime!.minute,
                    );
                    try {
                      await ApiService.post('/applications/interviews/', body: {
                        'application': selectedAppId,
                        'scheduled_at': scheduledAt.toUtc().toIso8601String(),
                        'duration_minutes': duration,
                        'location': locationCtrl.text,
                        'notes': notesCtrl.text,
                      });
                      if (ctx.mounted) Navigator.pop(ctx);
                      if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Собеседование назначено!')),
                        );
                      }
                      _load();
                    } catch (e) {
                      if (ctx.mounted) {
                        ScaffoldMessenger.of(ctx).showSnackBar(
                          const SnackBar(content: Text('Ошибка создания')),
                        );
                      }
                    }
                  },
                  child: const Text('Назначить'),
                ),
              ],
            );
          },
        );
      },
    );
    locationCtrl.dispose();
    notesCtrl.dispose();
  }
}
