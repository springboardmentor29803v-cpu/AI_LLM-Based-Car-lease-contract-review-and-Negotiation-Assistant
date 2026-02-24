import 'package:flutter/material.dart';

void main() => runApp(const LeaseAssistant());

class LeaseAssistant extends StatelessWidget {
  const LeaseAssistant({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.blue, useMaterial3: true),
      home: const Dashboard(),
    );
  }
}

class Dashboard extends StatelessWidget {
  const Dashboard({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Lease Assistant'),
        backgroundColor: Colors.blue.shade100,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text("Active Extractions", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            // THIS IS YOUR DATA CARD
            Card(
              elevation: 4,
              child: ListTile(
                leading: const Icon(Icons.directions_car, color: Colors.blue, size: 40),
                title: const Text("2023 Honda City", style: TextStyle(fontWeight: FontWeight.bold)),
                subtitle: const Text("VIN: 1N4AL3APXFC123456\nMonthly: \$485.00 | APR: 5.2%"),
                trailing: const Icon(Icons.check_circle, color: Colors.green),
                isThreeLine: true,
              ),
            ),
          ],
        ),
      ),
    );
  }
}