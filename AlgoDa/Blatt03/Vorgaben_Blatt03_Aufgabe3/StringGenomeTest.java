
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

public class StringGenomeTest {

	@Test
	public void testAddNucleotide() {
		StringGenome s = new StringGenome(); // 创建一个StringGenome对象
		assertDoesNotThrow(() -> s.addNucleotide('A')); // 测试合法核苷酸通过assertDoesNotThrow这个方式

		assertEquals( 1, s.length()); // 断言长度为1 是否正确

		assertDoesNotThrow(() -> s.addNucleotide('C'));
		assertDoesNotThrow(() -> s.addNucleotide('G'));
		assertDoesNotThrow(() -> s.addNucleotide('T'));

		assertThrows(RuntimeException.class() -> s.addNucleotide('X'))); // 测试非法核苷酸通过assertThrows这个方式

		try {

		s.addNucleotide('X');}
			} catch (RuntimeException e) {
				assertEquals("Illegal nucleotide", e.getMessage());
			}
	}

	@Test
	public void testNucleotideAt() {
	//TODO
		StringGenome s = new StringGenome();
		s.addNucleotide('A'); // 添加合法核苷酸
		assertEquals('A', s.nucleotideAt(0)); // 测试第一个核苷酸
	}


	@Test
	public void testLength() {
	//TODO

	}

	@Test
	public void testToString() {
	//TODO
	}

	@Test
	public void testEqualsObject() {
	//TODO
	}

}
