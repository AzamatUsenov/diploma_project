import 'dart:math';
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
              backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest,
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
      text = '${_fmt(min!)} - ${_fmt(max!)} сўм';
    } else if (max != null) {
      text = 'до ${_fmt(max!)} сўм';
    } else if (min != null) {
      text = 'от ${_fmt(min!)} сўм';
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
            Icon(icon, size: 64, color: Theme.of(context).hintColor.withAlpha(100)),
            const SizedBox(height: 16),
            Text(title, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Theme.of(context).hintColor)),
            if (subtitle != null) ...[
              const SizedBox(height: 8),
              Text(subtitle!, style: TextStyle(fontSize: 13, color: Theme.of(context).hintColor.withAlpha(150)), textAlign: TextAlign.center),
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

class ShimmerLoading extends StatefulWidget {
  final int itemCount;
  final Widget Function(BuildContext context, int index) itemBuilder;

  const ShimmerLoading({
    super.key,
    this.itemCount = 5,
    required this.itemBuilder,
  });

  factory ShimmerLoading.jobCards() => ShimmerLoading(itemBuilder: (ctx, _) => const _ShimmerJobCard());
  factory ShimmerLoading.simpleCards() => ShimmerLoading(itemBuilder: (ctx, _) => const _ShimmerSimpleCard());

  @override
  State<ShimmerLoading> createState() => _ShimmerLoadingState();
}

class _ShimmerLoadingState extends State<ShimmerLoading> with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 1500))..repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      listenable: _ctrl,
      builder: (ctx, _) => ListView.builder(
        padding: const EdgeInsets.all(16),
        physics: const NeverScrollableScrollPhysics(),
        itemCount: widget.itemCount,
        itemBuilder: (ctx, i) => _ShimmerWrapper(
          progress: _ctrl.value,
          child: widget.itemBuilder(ctx, i),
        ),
      ),
    );
  }
}

class AnimatedBuilder extends AnimatedWidget {
  final Widget Function(BuildContext context, Widget? child) builder;
  const AnimatedBuilder({super.key, required super.listenable, required this.builder});
  Animation<double> get animation => listenable as Animation<double>;
  @override
  Widget build(BuildContext context) => builder(context, null);
}

class _ShimmerWrapper extends StatelessWidget {
  final double progress;
  final Widget child;
  const _ShimmerWrapper({required this.progress, required this.child});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final baseColor = isDark ? Colors.grey.shade800 : Colors.grey.shade200;
    final highlightColor = isDark ? Colors.grey.shade700 : Colors.grey.shade100;

    return ShaderMask(
      shaderCallback: (bounds) {
        return LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [baseColor, highlightColor, baseColor],
          stops: [max(0, progress - 0.3), progress, min(1, progress + 0.3)],
        ).createShader(bounds);
      },
      blendMode: BlendMode.srcATop,
      child: child,
    );
  }
}

class _ShimmerJobCard extends StatelessWidget {
  const _ShimmerJobCard();

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              _box(180, 16), const Spacer(), _box(55, 22, radius: 8),
            ]),
            const SizedBox(height: 10),
            Row(children: [_box(100, 12), const SizedBox(width: 16), _box(80, 12)]),
            const SizedBox(height: 12),
            Row(children: [_box(70, 14), const SizedBox(width: 16), _box(40, 14), const SizedBox(width: 16), _box(50, 14)]),
            const SizedBox(height: 12),
            Row(children: [_box(50, 24, radius: 8), const SizedBox(width: 6), _box(60, 24, radius: 8), const SizedBox(width: 6), _box(45, 24, radius: 8)]),
          ],
        ),
      ),
    );
  }
}

class _ShimmerSimpleCard extends StatelessWidget {
  const _ShimmerSimpleCard();

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            _box(48, 48, radius: 12),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [_box(160, 14), const SizedBox(height: 8), _box(90, 12)],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

Widget _box(double w, double h, {double radius = 4}) => Container(
  width: w, height: h,
  decoration: BoxDecoration(color: Colors.grey, borderRadius: BorderRadius.circular(radius)),
);
