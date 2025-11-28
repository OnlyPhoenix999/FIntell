import 'package:flutter/material.dart';

const Color darkGray = Color(0xFF1F1F1F);
const Color cardGray = Color(0xFF2A2A2A);
const Color neonGreen = Color(0xFF00E676);

class AnalyticsPage extends StatelessWidget {
  const AnalyticsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Text(
            "Analytics",
            style: TextStyle(
              color: neonGreen,
              fontSize: 26,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 20),
          Text(
            "Spending Breakdown",
            style: TextStyle(color: Colors.white70, fontSize: 16),
          ),
          SizedBox(height: 10),
          Text(
            "Charts coming soon...",
            style: TextStyle(color: Colors.white54),
          ),
        ],
      ),
    );
  }
}
