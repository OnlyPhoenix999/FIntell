import 'dart:math';
import 'package:flutter/material.dart';

class MoneyRainSplash extends StatefulWidget {
  const MoneyRainSplash({super.key});

  @override
  State<MoneyRainSplash> createState() => _MoneyRainSplashState();
}

class _MoneyRainSplashState extends State<MoneyRainSplash>
    with TickerProviderStateMixin {
  final Random random = Random();
  late AnimationController logoController;
  late Animation<double> fadeAnim;
  late Animation<double> scaleAnim;
  late Animation<Offset> slideAnim;

  bool raining = true;

  // Placeholder image URL as per instructions
  static const String _imageUrl =
      "https://www.gstatic.com/flutter-onestack-prototype/genui/example_1.jpg";

  @override
  void initState() {
    super.initState();

    // LOGO ANIMATION (fade + slide + zoom)
    logoController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );

    fadeAnim = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: logoController, curve: Curves.easeOut),
    );

    scaleAnim = Tween<double>(begin: 0.4, end: 1.0).animate(
      CurvedAnimation(parent: logoController, curve: Curves.easeOutBack),
    );

    slideAnim = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(parent: logoController, curve: Curves.easeOut),
    );

    // Start logo animation after small delay
    Future<void>.delayed(const Duration(seconds: 1), () {
      logoController.forward();
    });

    // Stop rain after 3 seconds
    Future<void>.delayed(const Duration(seconds: 3), () {
      setState(() => raining = false);
    });
  }

  @override
  void dispose() {
    logoController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: <Widget>[
          // ------------------ MONEY RAIN ------------------
          if (raining) ...List<Widget>.generate(30, (int i) => fallingMoney(i)),

          // ------------------ CENTER LOGO ------------------
          Center(
            child: SlideTransition(
              position: slideAnim,
              child: FadeTransition(
                opacity: fadeAnim,
                child: ScaleTransition(
                  scale: scaleAnim,
                  child: Image.network(
                    _imageUrl, // Replaced Image.asset with Image.network
                    width: 140,
                    errorBuilder: (BuildContext context, Object error,
                        StackTrace? stackTrace) {
                      return const SizedBox(
                        width: 140,
                        height: 140,
                        child: Icon(Icons.error, color: Colors.red),
                      );
                    },
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ------------------ COIN + NOTE DROP ------------------
  Widget fallingMoney(int index) {
    double startX = random.nextDouble() * MediaQuery.of(context).size.width;

    double speed = 3 + random.nextDouble() * 3;

    return AnimatedBuilder(
      animation: logoController,
      builder: (BuildContext context, Widget? child) {
        double top = (logoController.value * speed * 600) %
            (MediaQuery.of(context).size.height + 100); // Ensure money falls off screen

        return Positioned(
          left: startX,
          top: top,
          child: SizedBox(
            width: random.nextBool() ? 30 : 45,
            child: Image.network(
              _imageUrl, // Replaced Image.asset with Image.network
              errorBuilder:
                  (BuildContext context, Object error, StackTrace? stackTrace) {
                return Icon(
                  Icons.monetization_on, // Placeholder icon for falling money
                  color: Colors.yellow.shade700,
                  size: random.nextBool() ? 30 : 45,
                );
              },
            ),
          ),
        );
      },
    );
  }
}

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: const MoneyRainSplash(),
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
    );
  }
}