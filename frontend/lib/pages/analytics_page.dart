import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class AnalyticsPage extends StatefulWidget {
  const AnalyticsPage({super.key});

  @override
  State<AnalyticsPage> createState() => _AnalyticsPageState();
}

class _AnalyticsPageState extends State<AnalyticsPage> {
  final Color darkGray = const Color(0xFF1F1F1F);
  final Color cardGray = const Color(0xFF2A2A2A);
  final Color neonGreen = const Color(0xFF00E676);

  bool loading = false;
  String? errorMessage;
  Map<String, dynamic>? insights;

  // -----------------------
  // SYNC DATA
  // -----------------------
  Future<void> syncData() async {
    setState(() {
      loading = true;
      errorMessage = null;
    });

    try {
      final url = Uri.parse(
        "http://10.0.2.2:9000/fiu/sync/maverick/maverick@aa",
      );

      final response = await http.get(url);

      if (response.statusCode != 200) {
        throw Exception("Sync failed: ${response.body}");
      }

      await fetchInsights();
    } catch (e) {
      setState(() => errorMessage = e.toString());
    }

    setState(() => loading = false);
  }

  // -----------------------
  // FETCH INSIGHTS
  // -----------------------
  Future<void> fetchInsights() async {
    try {
      final url = Uri.parse("http://10.0.2.2:9000/fiu/insights/maverick");

      final response = await http.get(url);

      if (response.statusCode != 200) {
        throw Exception("Insights fetch failed: ${response.body}");
      }

      final jsonData = jsonDecode(response.body);

      setState(() {
        insights = jsonData["latest"];
      });
    } catch (e) {
      setState(() => errorMessage = e.toString());
    }
  }

  @override
  void initState() {
    super.initState();
    fetchInsights();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: darkGray,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "Analytics",
                style: TextStyle(
                  color: neonGreen,
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 12),

              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: neonGreen,
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 14,
                  ),
                ),
                onPressed: loading ? null : syncData,
                child: loading
                    ? const CircularProgressIndicator(color: Colors.black)
                    : const Text("Sync Data", style: TextStyle(fontSize: 16)),
              ),

              const SizedBox(height: 20),

              if (errorMessage != null)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.red.shade700,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    errorMessage!,
                    style: const TextStyle(color: Colors.white),
                  ),
                ),

              const SizedBox(height: 16),

              Expanded(
                child: insights == null
                    ? const Center(
                        child: Text(
                          "No insights yet.\nClick Sync.",
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.white70, fontSize: 16),
                        ),
                      )
                    : insightsUI(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget insightsUI() {
    final insightData = insights!["insights"] ?? {};

    return ListView(
      children: [
        infoCard("Generated At", insights!["generatedAt"]),
        ...insightData.entries.map((e) {
          return infoCard(e.key.toString(), e.value.toString());
        }),
      ],
    );
  }

  Widget infoCard(String title, String value) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: cardGray,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: neonGreen.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              color: neonGreen,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(color: Colors.white, fontSize: 15),
          ),
        ],
      ),
    );
  }
}
