import 'package:flutter/material.dart';
import '../widgets/quick_action_button.dart';
import '../pages/analytics_page.dart';
import '../pages/transactions_page.dart';

const Color darkGray = Color(0xFF1F1F1F);
const Color cardGray = Color(0xFF2A2A2A);
const Color neonGreen = Color(0xFF00E676);

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [
      const HomeDashboard(),
      const TransactionsPage(),
      const AddPlaceholder(),
      const AnalyticsPage(),
      const ProfilePlaceholder(),
    ];

    return Scaffold(
      backgroundColor: darkGray,
      body: SafeArea(child: pages[_selectedIndex]),
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: cardGray,
        selectedItemColor: neonGreen,
        unselectedItemColor: Colors.white54,
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: (i) => setState(() => _selectedIndex = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: "Home"),
          BottomNavigationBarItem(
            icon: Icon(Icons.receipt_long),
            label: "Transactions",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.add_circle_outline),
            label: "Add",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.bar_chart),
            label: "Analytics",
          ),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: "Profile"),
        ],
      ),
    );
  }
}

class HomeDashboard extends StatelessWidget {
  const HomeDashboard({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const SizedBox(height: 20),
        const Text(
          "FinanceFlow",
          style: TextStyle(
            color: neonGreen,
            fontSize: 32,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 5),
        const Text(
          "Track • Analyse • Grow",
          style: TextStyle(color: Colors.white70),
        ),

        const SizedBox(height: 25),

        // QUICK ACTIONS
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: const [
            QuickActionButton(
              icon: Icons.remove_circle,
              text: "Expense",
              neonGreen: neonGreen,
            ),
            QuickActionButton(
              icon: Icons.add_circle,
              text: "Income",
              neonGreen: neonGreen,
            ),
            QuickActionButton(
              icon: Icons.bar_chart,
              text: "Analytics",
              neonGreen: neonGreen,
            ),
          ],
        ),

        const SizedBox(height: 25),

        // BALANCE CARD
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: cardGray,
              borderRadius: BorderRadius.circular(22),
              border: Border.all(color: neonGreen.withOpacity(0.4)),
            ),
            child: Column(
              children: const [
                OverviewItem("💰 Wallet Balance", "₹ 14,200"),
                SizedBox(height: 10),
                OverviewItem("📉 Expenses (Month)", "₹ 4,500"),
                SizedBox(height: 10),
                OverviewItem("📈 Income (Month)", "₹ 8,200"),
              ],
            ),
          ),
        ),

        const SizedBox(height: 25),
        const Align(
          alignment: Alignment.centerLeft,
          child: Padding(
            padding: EdgeInsets.symmetric(horizontal: 16),
            child: Text(
              "Recent Activity",
              style: TextStyle(
                color: neonGreen,
                fontWeight: FontWeight.bold,
                fontSize: 18,
              ),
            ),
          ),
        ),

        const SizedBox(height: 10),

        // RECENT TRANSACTIONS LIST
        Expanded(
          child: ListView(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            children: const [
              TransactionTile("Bought Groceries", "₹ 320", false),
              TransactionTile("Freelance Work", "₹ 5,000", true),
              TransactionTile("Snacks", "₹ 80", false),
            ],
          ),
        ),
      ],
    );
  }
}

class OverviewItem extends StatelessWidget {
  final String label, value;
  const OverviewItem(this.label, this.value, {super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Colors.white70)),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
      ],
    );
  }
}

class TransactionTile extends StatelessWidget {
  final String title, amount;
  final bool isIncome;

  const TransactionTile(this.title, this.amount, this.isIncome, {super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: cardGray,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 22,
            backgroundColor: isIncome
                ? Colors.greenAccent.withOpacity(0.15)
                : Colors.redAccent.withOpacity(0.15),
            child: Icon(
              isIncome ? Icons.arrow_downward : Icons.arrow_upward,
              color: isIncome ? Colors.greenAccent : Colors.redAccent,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(color: Colors.white, fontSize: 16),
                ),
                const SizedBox(height: 4),
                const Text(
                  "Today",
                  style: TextStyle(color: Colors.white38, fontSize: 12),
                ),
              ],
            ),
          ),
          Text(
            amount,
            style: TextStyle(
              color: isIncome ? Colors.greenAccent : Colors.redAccent,
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
        ],
      ),
    );
  }
}

class AddPlaceholder extends StatelessWidget {
  const AddPlaceholder({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text(
        "Add Transaction Page Coming Soon...",
        style: TextStyle(color: Colors.white, fontSize: 20),
      ),
    );
  }
}

class ProfilePlaceholder extends StatelessWidget {
  const ProfilePlaceholder({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text(
        "Profile Page Coming Soon...",
        style: TextStyle(color: Colors.white, fontSize: 20),
      ),
    );
  }
}
