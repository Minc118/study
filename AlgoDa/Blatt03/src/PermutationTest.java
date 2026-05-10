import java.util.LinkedList;
import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class PermutationTest {
	PermutationVariation p1; // Declare p1 as PermutationVariation type
	PermutationVariation p2; // 测试用的第二个对象
	public int n1; // 用于测试的第一个对象的大小
	public int n2; // 用于测试的第二个对象的大小
	int cases=1; // 用于测试的用例编号

	//初始化两个测试对象，避免测试互相干扰，每个测试方法都需要调用这个方法
	void initialize() {
		n1=4; // 用于测试的第一个对象的大小 - 可以根据需要调整
		n2=6; // 用于测试的第二个对象的大小 - 可以根据需要调整
		Cases c= new Cases(); // 创建一个Cases对象，用于切换测试用例
		p1= c.switchforTesting(cases, n1); //生成第一个测试对象p1
		p2= c.switchforTesting(cases, n2); //生成第二个测试对象p2
	}

    //
	@Test
	void testPermutation() {
		initialize(); // 初始化p1和p2

		assertNotNull(p1.original, "p1 should not be null");
		assertNotNull(p2.original, "p2 should not be null");
		//长度检查
		assertEquals(n1, p1.original.length);
		assertEquals(n2, p2.original.length);
		//无重复检查
		assertTrue(noTwoSame(p1.original), "p1 should not have two same elements");
		assertTrue(noTwoSame(p2.original), "p2 should not have two same elements");
		// allDerangements初始化检查
		assertNotNull(p1.allDerangements, "p1 should not be null");
		assertNotNull(p2.allDerangements, "p2 should not be null");

		assertTrue(p1.allDerangements.isEmpty(), "p1 should have no derangements initially");
		assertTrue(p2.allDerangements.isEmpty(), "p2 should have no derangements initially");
	}

	@Test
	void testDerangements() {

		initialize();
		//in case there is something wrong with the constructor
		// 重新初始化以确保测试的正确性
		fixConstructor();
		// 测试无定点排列数量
		p1.derangements();
		assertEquals(derangementCountMathPow(n1), p1.allDerangements.size()); // 检查p1的无定点排列数量是否正确
		for ( int[] arr : p1.allDerangements ) {
			assertTrue(noSameRange(arr, p1.original), "p1 should not have any elements in the original position"); // 检查p1的无定点排列是否没有元素在原位
		}

		p2.derangements();
		assertEquals(derangementCountMathPow(n2), p2.allDerangements.size()); // 检查p2的无定点排列数量是否正确
		for ( int[] arr : p2.allDerangements ) {
			assertTrue(noSameRange(arr, p2.original), "p2 should not have any elements in the original position"); // 检查p2的无定点排列是否没有元素在原位
		}
	}
	
	@Test
	void testsameElements() {
		initialize();
		//in case there is something wrong with the constructor
		fixConstructor();
		// Test same elements in original arrays
		p1.derangements();
		assertNotNull(p1.allDerangements, "allDerangements should not be null after derangements");
		assertFalse(p1.allDerangements.isEmpty(), "allDerangements should not be empty after derangements");
		for (int[] arr : p1.allDerangements) {
			assertTrue(notSameOrder(arr, p1.original), "p1's derangements should not be in the same order as original"); // 检查p1的无定点排列是否不是原始顺序
		}

		p2.derangements();
		assertNotNull(p2.allDerangements, "allDerangements should not be null after derangements");
		assertFalse(p2.allDerangements.isEmpty(), "allDerangements should not be empty after derangements");
		for (int[] arr : p2.allDerangements) {
			assertTrue(notSameOrder(arr, p2.original), "p2's derangements should not be in the same order as original"); // 检查p2的无定点排列是否不是原始顺序
		}
	}

    //辅助函数

	//快速切换PermutationVariation的测试用例
	void setCases(int c) {
		this.cases=c; // 设置测试用例编号
	}
	
	public void fixConstructor() {
		//in case there is something wrong with the constructor
		p1.allDerangements=new LinkedList<int[]>();
		for(int i=0;i<n1;i++)
			p1.original[i]=2*i+1;
		
		p2.allDerangements=new LinkedList<int[]>();
		for(int i=0;i<n2;i++)
			p2.original[i]=i+1;
	}

	// 判断是否数组中没有两个相同的元素，true表示没有相同元素，false表示有相同元素
	boolean noTwoSame(int[] arr) {
		// 检查数组中是否有两个相同的元素
		for (int i = 0; i < arr.length; i++) {
			for (int j = i + 1; j < arr.length; j++) {
				if (arr[i] == arr[j]) {
					return false; // 如果找到相同的元素，返回false
				}
			}
		}
		return true; // 如果没有找到相同的元素，返回true
	}

	//测试一个排列是不是original的乱序（derangement）排列 - 无任何元素在原位
	boolean noSameRange(int[] arr, int[] arr2) {
		//检查数组中元素是否在原位
		if (arr.length != arr2.length) {
			return false; // 如果数组长度不等于original的长度，返回false
		}
		for (int i = 0; i < arr.length; i++) {
			if (arr[i] == arr2[i]) {
				return false; // 如果有元素在原位，返回false
			}
		}
		return true; // 如果没有元素在原位，返回true
	}

	//测试两个数组是不是全排列的关系，即一个数组是另一个数组的乱序排列 - 内部元素相同但顺序不同
	boolean notSameOrder(int[] arr1, int[] arr2) {
		// 检查两个数组是否是全排列的关系
		if (arr1.length != arr2.length) {
			return false; // 如果长度不相等，返回false
		}
		// 克隆两个数组以避免修改原数组
		int[] same1 = arr1.clone(); // 克隆第一个数组
		int[] same2 = arr2.clone(); // 克隆第二个数组
		// 对两个数组进行排序
		Arrays.sort(arr1); // 对第一个数组进行排序
		Arrays.sort(arr2); // 对第二个数组进行排序
		return Arrays.equals(arr1, arr2); // 比较两个排序后的数组是否相等
	}

	//计算无定点排列数量用于确定测试的正确性 - 不会做太少的测试或者做太多的测试
	//方法1 ：D(n) = n! * sum_{k=0}^n (-1)^k / k! - 公式
	//方法2 ：D(n) = (n-1) * (D(n-1) + D(n-2)) - 递推公式
	int derangementCount(int n) {
		if (n == 0) return 1; // D(0) = 1 - 排列长度为空排列 - 只有一种方式
		if (n == 1) return 0; // D(1) = 0 - 只有一个元素的排列没有无定点排列，不可能不让他不在原位
		int[] dp = new int[n + 1]; // 创建一个数组来存储D(n)的值 - 数组长度为n+1
		dp[0] = 1; // D(0) // 空排列的无定点排列数量为1
		dp[1] = 0; // D(1) // 只有一个元素的排列没有无定点排列数量为0
		for (int i = 2; i <= n; i++) { // 从2开始计算到n - 计算D(n)的值
			dp[i] = (i - 1) * (dp[i - 1] + dp[i - 2]); // D(n) = (n-1) * (D(n-1) + D(n-2)) - 递推公式
		}
		return dp[n]; // 返回D(n)
	}

	//计算阶乘 - 用于计算排列数量
	int faku(int n) {
		int re = 1;
		for (int i = 2; i <= n; i++) {
			re *= i;
		}
		return re;
	}

	//计算无定点排列的数量
	int derangementCountMathPow(int n) {
		// D(n) = n! * sum_{k=0}^n (-1)^k / k!
		double sum = 0.0; // 初始化求和变量
		for (int k = 0; k <= n; k++) {
			sum += Math.pow(-1, k) / faku(k); // 计算 (-1)^k / k! 并累加到sum
		}
		return (int) Math.round(faku(n) * sum); // 返回 D(n) 的值，四舍五入
	}

}



