import 'package:flutter/material.dart';

class QuickActionButton extends StatelessWidget {
  final IconData icon;
  final String text;
  final Color neonGreen;

  const QuickActionButton({
    super.key,
    required this.icon,
    required this.text,
    required this.neonGreen,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: const Color(0xFF2A2A2A),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: neonGreen, size: 30),
        ),
        const SizedBox(height: 8),
        Text(text, style: const TextStyle(color: Colors.white70)),
      ],
    );
  }
}
