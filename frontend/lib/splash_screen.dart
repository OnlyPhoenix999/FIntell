import 'dart:math';
import 'package:flutter/material.dart';
import 'home/home_page.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with TickerProviderStateMixin {
  final Random random = Random();

  late AnimationController logoController;
  late Animation<double> fadeAnim;
  late Animation<double> scaleAnim;
  late Animation<Offset> slideAnim;

  late AnimationController rainController;
  bool raining = true;

  static const String _imageUrl =
      "https://www.gstatic.com/flutter-onestack-prototype/genui/example_1.jpg";

  final List<String> coinAssets = ["Assests/coins/dollar.png"];
  final List<String> noteAssets = ["Assests/notes/note.png"];

  @override
  void initState() {
    super.initState();

    logoController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );

    fadeAnim = Tween(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(parent: logoController, curve: Curves.easeOut));

    scaleAnim = Tween(begin: 0.6, end: 1.0).animate(
      CurvedAnimation(parent: logoController, curve: Curves.easeOutBack),
    );

    slideAnim = Tween(
      begin: const Offset(0, 0.2),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: logoController, curve: Curves.easeOut));

    Future.delayed(const Duration(milliseconds: 500), () {
      logoController.forward();
    });

    rainController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat();

    Future.delayed(const Duration(seconds: 4), () {
      if (mounted) setState(() => raining = false);
    });

    logoController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        Future.delayed(const Duration(milliseconds: 800), () {
          if (!mounted) return;
          Navigator.pushReplacement(
            context,
            PageRouteBuilder(
              transitionDuration: const Duration(milliseconds: 600),
              pageBuilder: (_, __, ___) => const HomePage(),
              transitionsBuilder: (_, animation, __, child) {
                return SlideTransition(
                  position: animation.drive(
                    Tween(
                      begin: const Offset(1, 0),
                      end: Offset.zero,
                    ).chain(CurveTween(curve: Curves.easeOutCubic)),
                  ),
                  child: child,
                );
              },
            ),
          );
        });
      }
    });
  }

  @override
  void dispose() {
    logoController.dispose();
    rainController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          if (raining) ...List.generate(32, (i) => fallingMoney(i)),
          Center(
            child: SlideTransition(
              position: slideAnim,
              child: FadeTransition(
                opacity: fadeAnim,
                child: ScaleTransition(
                  scale: scaleAnim,
                  child: Image.network(_imageUrl, width: 150),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget fallingMoney(int index) {
    final w = MediaQuery.of(context).size.width;
    final h = MediaQuery.of(context).size.height;

    double startX = random.nextDouble() * w;
    double speed = 0.7 + random.nextDouble() * 0.6;
    double rotation = random.nextDouble() * 0.8 - 0.4;

    String img = index.isEven ? coinAssets[0] : noteAssets[0];

    return AnimatedBuilder(
      animation: rainController,
      builder: (_, __) {
        double y = (rainController.value * (h + 150) * speed) % (h + 150);

        return Positioned(
          left: startX,
          top: y,
          child: Transform.rotate(
            angle: rainController.value * rotation,
            child: Image.asset(img, width: index.isEven ? 32 : 55),
          ),
        );
      },
    );
  }
}
