import 'package:flutter/material.dart';

class LevelBadge extends StatelessWidget {
  final String level;
  const LevelBadge(this.level, {super.key});

  @override
  Widget build(BuildContext context) {
    final config = {
      'junior': (Colors.green, 'Junior'),
      'mid': (Colors.blue, 'Middle'),
      'senior': (Colors.purple, 'Senior'),
    };
    final (color, label) = config[level] ?? (Colors.grey, level);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withAlpha(25),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withAlpha(60)),
      ),
      child: Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: color.shade700)),
    );
  }
}

class HonestyIndicator extends StatelessWidget {
  final int score;
  final bool showBar;
  const HonestyIndicator(this.score, {this.showBar = false, super.key});

  @override
  Widget build(BuildContext context) {
    final color = score >= 70 ? Colors.green : score >= 40 ? Colors.orange : Colors.red;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('$score%', style: TextStyle(fontWeight: FontWeight.bold, color: color.shade700, fontSize: 14)),
        if (showBar) ...[
          const SizedBox(height: 4),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: score / 100,
              backgroundColor: Colors.grey.shade200,
              color: color,
              minHeight: 4,
            ),
          ),
        ],
      ],
    );
  }
}

class SalaryText extends StatelessWidget {
  final int? min;
  final int? max;
  const SalaryText({this.min, this.max, super.key});

  String _fmt(int n) => n >= 1000000 ? '${(n / 1000000).toStringAsFixed(1)}M' : '${(n / 1000).round()}K';

  @override
  Widget build(BuildContext context) {
    String text;
    if (min != null && max != null) {
      text = '${_fmt(min!)} - ${_fmt(max!)} ₸';
    } else if (max != null) {
      text = 'до ${_fmt(max!)} ₸';
    } else if (min != null) {
      text = 'от ${_fmt(min!)} ₸';
    } else {
      text = 'Не указана';
    }
    return Text(text, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14));
  }
}

class EmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  const EmptyState({required this.icon, required this.title, this.subtitle, super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(48),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 64, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            Text(title, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Colors.grey.shade600)),
            if (subtitle != null) ...[
              const SizedBox(height: 8),
              Text(subtitle!, style: TextStyle(fontSize: 13, color: Colors.grey.shade500), textAlign: TextAlign.center),
            ],
          ],
        ),
      ),
    );
  }
}

class SkillChip extends StatelessWidget {
  final String label;
  final Color? color;
  const SkillChip(this.label, {this.color, super.key});

  @override
  Widget build(BuildContext context) {
    final c = color ?? Theme.of(context).colorScheme.primary;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: c.withAlpha(20),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: c)),
    );
  }
}
