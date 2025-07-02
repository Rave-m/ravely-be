from helper.recommendations import get_recommendations_by_name

print('=== Testing Recommendations ===')
result = get_recommendations_by_name('Candi Sambisari', 5)
print(f'Recommendations for Candi Sambisari ({len(result)} items):')
for i, rec in enumerate(result, 1):
    print(f'{i}. {rec["nama_destinasi"]} - {rec["kabupaten"]}')
    print(f'   URL: {rec["alamat"]}')
    print()

print('\n=== Testing Another Destination ===')    
result2 = get_recommendations_by_name('Waterboom Jogja', 3)
print(f'Recommendations for Waterboom Jogja ({len(result2)} items):')
for i, rec in enumerate(result2, 1):
    print(f'{i}. {rec["nama_destinasi"]} - {rec["kabupaten"]}')
    print()
